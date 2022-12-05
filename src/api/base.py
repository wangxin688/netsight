from dataclasses import asdict
from datetime import datetime
from typing import Generic, Optional, TypeVar

import pydantic
from fastapi.encoders import jsonable_encoder
from pydantic.dataclasses import dataclass
from pydantic.generics import GenericModel


def default(obj):
    if isinstance(obj, datetime):
        return int(obj.timestamp())


class BaseModel(pydantic.BaseModel):
    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }  # method for customer JSON encoding of datetime fields


DataT = TypeVar("DataT", bound=BaseModel)


class BaseResponse(GenericModel, Generic[DataT]):
    code: int
    data: Optional[DataT] = None
    msg: str

    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }  # method for customer JSON encoding of datetime fields


class ListData(GenericModel, Generic[DataT]):
    count: int
    results: Optional[DataT]


class BaseListResponse(GenericModel, Generic[DataT]):
    code: int
    data: ListData
    msg: str

    class Config:
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }  # method for customer JSON encoding of datetime fields


class CommonQueryParams:
    def __init__(
        self,
        limit: int = 20,
        offset: int | None = 0,
        q: str | None = None,
    ):
        self.limit = limit
        self.offset = offset
        self.q = q


@dataclass
class BaseQuery:
    def dict(self):
        return asdict(self)
