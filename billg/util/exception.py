from fastapi import HTTPException
from typing import Optional


class CustomException(HTTPException):
    def __init__(
        self,
        status_code: int,
        code: str,
        message: Optional[str] = None,
    ):
        super().__init__(status_code=status_code, detail=message or "")
        self.code = code
