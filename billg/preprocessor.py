import cv2
import numpy as np


class OCRImagePreprocessor:
    def __init__(self):
        pass

    def preprocess(self, image_bytes: bytes) -> bytes:
        """
        OpenCV를 이용해 그레이스케일, 노이즈 제거, 이진화 등 전처리를 수행한 뒤
        JPEG 바이트로 반환.
        """
        # 1) 바이트 → NumPy 배열 → BGR 이미지
        arr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(arr, cv2.IMREAD_COLOR)
        if img is None:
            raise ValueError("이미지 디코딩 실패")

        # 2) 그레이스케일
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # 3) 노이즈 제거 (bilateral filter)
        denoised = cv2.bilateralFilter(gray, d=9, sigmaColor=75, sigmaSpace=75)

        # 4) 적응형 이진화
        thresh = cv2.adaptiveThreshold(
            denoised,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            blockSize=11,
            C=2,
        )

        # 5) 작은 잡음 제거용 형태학적 오프닝
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        opened = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

        # 6) 다시 JPEG 바이트로 인코딩
        success, buf = cv2.imencode(".jpg", opened)
        if not success:
            raise ValueError("이미지 인코딩 실패")
        return buf.tobytes()
