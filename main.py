import os
import logging
import time
import base64
import json
import asyncio
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


TEMPLATE = """
당신은 영수증에서 특정 항목을 추출하는 OCR 전문가입니다.
아래 제공된 영수증 이미지에서 지정된 항목만 정확히 추출하여 JSON 형식으로 출력하세요.
추출할 항목:
{columns}
응답 규칙:
- 반드시 JSON 형식으로만 출력합니다.
- 날짜 및 시간 정보가 포함된 항목이 있으면 "YYYY-MM-DD HH:MM:SS" 형식으로 반환합니다.
- 이미지에 항목이 존재하지 않으면, 문자열 항목은 빈 문자열(""), 숫자 항목은 숫자 0으로 응답합니다.
- 추가적인 설명, 코멘트, 부가 정보는 일절 포함하지 않습니다.
- 영수증에서 실제로 확인된 정보만 응답하고, 추측하지 마세요.
- 모든 키는 요청한 항목과 정확히 일치해야 합니다.
"""


async def ocr(columns: List[str], file: UploadFile):
    try:
        image_bytes = await file.read()
        # image_bytes = preprocessor.preprocess(image_bytes)
        base64_image = encode_image(image_bytes)
        response = await openai.chat.completions.create(
            model="gpt-4.1-mini",
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
            max_tokens=4096,
            response_format={"type": "json_object"},
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
