import humps
from pydantic import BaseModel


def camel_transform(string: str) -> str:
    return humps.camelize(string)


class BaseSchema(BaseModel):
    class Config:
        alias_generator = camel_transform
        populate_by_name = True
