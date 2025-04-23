import os
import logging
import time
import base64
import json
import asyncio
import cv2
import numpy as np

from typing import List
from billg.util import CustomException, limits, get_client_ip
from billg.preprocessor import OCRImagePreprocessor
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, Request, File, UploadFile
from openai import AsyncOpenAI

profile = os.environ.get("PYTHON_ENV", "local")
logger = logging.getLogger(__name__)

openai = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
app = FastAPI()
preprocessor = OCRImagePreprocessor()

EXCLUDE_PATHS = ["/actuator", "/docs", "/openapi.json"]


@app.middleware("http")
async def log_requests(request, call_next):
    if any(request.url.path.startswith(path) for path in EXCLUDE_PATHS):
        return await call_next(request)

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    logger.info(
        f"[Request][{get_client_ip(request)}]: {request.method} {request.url} - Time: {process_time:.4f}s"
    )
    return response


@app.exception_handler(CustomException)
async def custom_exception_handler(request: Request, exc: CustomException):
    logger.error(exc)
    custom_code = getattr(exc, "code", "HTTP_EXCEPTION")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "code": custom_code,
            "message": exc.detail,
            "status": exc.status_code,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(exc, exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"message": "서버 내부 오류가 발생했습니다. 관리자에게 문의하세요."},
    )


if profile == "local":
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["https://YOUR_SERVER_URL"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )


@app.get("/actuator/health/liveness")
async def liveness():
    return {"message": "OK"}


@app.get("/actuator/health/readiness")
async def readiness():
    return {"message": "OK"}


def encode_image(image_bytes):
    return base64.b64encode(image_bytes).decode("utf-8")


async def resize_image(image_bytes: bytes, size=(1024, 1024), quality=80) -> bytes:
    def sync_resize():
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_GRAYSCALE)
        img = cv2.resize(img, size, interpolation=cv2.INTER_AREA)
        _, buf = cv2.imencode(".jpg", img, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
        return buf.tobytes()

    return await asyncio.to_thread(sync_resize)


TEMPLATE = """
다음 이미지는 영수증이다. 이 이미지에서 다음 항목만 정확히 추출해서 JSON 형식으로 출력해줘.
추출할 항목: {columns}
단, 위 항목 중 날짜 및 시간 정보가 포함된 항목이 있다면 반드시 "YYYY-MM-DD HH:MM:SS" 형식으로 반환해라.
다른 추가적인 설명이나 부가정보는 일절 넣지 말고, 주어진 항목에 대해서만 JSON 키와 값으로 정확히 응답해라.
만약 항목이 이미지에 없으면 해당 항목의 값을 빈 문자열, 또는 숫자의 경우 0으로 응답해라.
"""


async def ocr(columns: List[str], file: UploadFile):
    try:
        image_bytes = await file.read()
        # TODO: resize 클라단에서 처리하고 보내는게 더 나을거같은데
        image_bytes = await resize_image(image_bytes)

        base64_image = encode_image(image_bytes)
        response = await openai.chat.completions.create(
            model="gpt-4.1",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": TEMPLATE.format(columns=columns),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                },
            ],
            max_tokens=8192,
            response_format={"type": "json_object"},
        )
        usage = response.usage
        logger.info(
            f"""

================================ OCR =================================
{file.filename}
{response.choices[0].message.content}

Prompt Tokens: {usage.prompt_tokens}
Completion Tokens: {usage.completion_tokens}
Total Tokens: {usage.total_tokens}
======================================================================

"""
        )

        return json.loads(response.choices[0].message.content)

    except Exception as e:
        logger.error(f"OCR 처리 중 오류 발생 ({file.filename}): {e}")
        raise e


@limits(calls=10, period_seconds=60)
@app.post("/scan")
async def scan(columns: List[str], files: List[UploadFile] = File(...)):
    tasks = [ocr(columns, file) for file in files]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    # 예외 처리 결과를 로깅하고 빈 결과를 반환
    processed_results = []
    for idx, result in enumerate(results):
        if isinstance(result, Exception):
            logger.error(f"파일 처리 중 오류 발생 ({files[idx].filename}): {result}")
            processed_results.append({})
        else:
            processed_results.append(result)

    return {"results": processed_results}
