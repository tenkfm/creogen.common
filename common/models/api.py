from typing import Generic, TypeVar, Optional
from pydantic.generics import GenericModel

T = TypeVar("T")

class ResponseObject(GenericModel, Generic[T]):
    status: str
    error: Optional[str] = None
    data: Optional[T] = None