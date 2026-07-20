from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar("T")


class APIResponse(BaseModel, Generic[T]):
    data: Optional[T] = None
    error: Optional[dict] = None

    @classmethod
    def ok(cls, data: T) -> "APIResponse[T]":
        return cls(data=data, error=None)

    @classmethod
    def fail(cls, code: str, message: str) -> "APIResponse[None]":
        return cls(data=None, error={"code": code, "message": message})
