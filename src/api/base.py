from datetime import datetime
from typing import Generic, Optional, TypeVar

import orjson
import pydantic
from fastapi.encoders import jsonable_encoder
from pydantic.generics import GenericModel


def default(obj):
    if isinstance(obj, datetime):
        return int(obj.timestamp())


def orjson_dumps(v, *, default=default):
    # orjson.dumps returns bytes, to match standard json.dumps we need to decode
    return orjson.dumps(v, default=default).decode()


class BaseModel(pydantic.BaseModel):
    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }  # method for customer JSON encoding of datetime fields

    def serializable_dict(self, **kwargs):
        default_dict = super().dict(**kwargs)
        return jsonable_encoder(default_dict)


DataT = TypeVar("DataT", bound=BaseModel)


class BaseResponse(GenericModel, Generic[DataT]):
    code: int
    data: Optional[DataT] = None
    msg: str

    class Config:
        json_loads = orjson.loads
        json_dumps = orjson_dumps
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
        json_loads = orjson.loads
        json_dumps = orjson_dumps
        json_encoders = {
            datetime: lambda v: int(v.timestamp())
        }  # method for customer JSON encoding of datetime fields
