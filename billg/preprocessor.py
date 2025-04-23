import cv2
import numpy as np


class OCRImagePreprocessor:
    def preprocess(self, image_bytes: bytes) -> bytes:
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("이미지 디코딩 실패")

        # 1) 그레이스케일
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 2) 노이즈 제거 (Gaussian blur가 텍스트 대비 유지에 더 적합)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)

        # 3) 대비 강조 (CLAHE - Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(blurred)

        # 4) 적응형 이진화
        thresh = cv2.adaptiveThreshold(
            enhanced,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=15,  # 블록 사이즈 증가로 더 안정적인 결과
            C=10,  # Threshold 조정
        )

        # 5) 형태학적 연산 (잡음 제거를 위한 opening)
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # 6) 결과 JPEG 인코딩
        success, buf = cv2.imencode(".jpg", cleaned)
        if not success:
            raise ValueError("이미지 인코딩 실패")
        return buf.tobytes()
