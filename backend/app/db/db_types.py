import uuid
from datetime import date, datetime
from ipaddress import (
    IPv4Address,
    IPv4Interface,
    IPv4Network,
    IPv6Address,
    IPv6Interface,
    IPv6Network,
    ip_address,
    ip_interface,
    ip_network,
)
from typing import Annotated, TypeAlias, no_type_check

from sqlalchemy import Boolean, Date, DateTime, Dialect, Integer, String, func, type_coerce
from sqlalchemy.dialects.postgresql import BYTEA, CIDR, HSTORE, INET, UUID
from sqlalchemy.ext.mutable import MutableDict
from sqlalchemy.orm import mapped_column
from sqlalchemy.sql import expression
from sqlalchemy.sql.elements import BindParameter, ColumnElement
from sqlalchemy.types import TypeDecorator

from app._types import VisibleName
from app.config import settings

IPvAnyInterface: TypeAlias = IPv4Interface | IPv6Interface
IPvAnyAddress: TypeAlias = IPv4Address | IPv6Address
IPvAnyNetwork: TypeAlias = IPv4Network | IPv6Network


class EncryptedString(TypeDecorator):
    impl = BYTEA
    cache_ok = True

    def __init__(self, secret_key: str | None = settings.SECRET_KEY) -> None:
        super().__init__()
        self.secret = secret_key

    @no_type_check
    def bind_expression(self, bind_value: BindParameter) -> ColumnElement | None:
        bind_value = type_coerce(bind_value, String)
        return func.pgp_sym_encrypt(bind_value, self.secret)

    @no_type_check
    def column_expression(self, column: ColumnElement) -> ColumnElement | None:
        return func.pgp_sym_decrypt(column, self.secret)


class PgIpInterface(TypeDecorator):
    """
    A codec for :py:mod:`ipaddress` interfaces.
    """

    impl = INET

    def process_bind_param(self, value: IPvAnyInterface | None, dialect: Dialect) -> str | None:
        return str(value) if value else None

    def process_result_value(self, value: IPvAnyInterface | None, dialect: Dialect) -> IPvAnyInterface | None:
        return ip_interface(value) if value else None

    def process_literal_param(self, value: str | None, dialect: Dialect) -> str:
        raise NotImplementedError("Not yet implemented")


class PgIpAddress(TypeDecorator):
    """
    A codec for :py:mod:`ipaddress` IP addresses.
    """

    impl = INET

    def process_bind_param(self, value: IPvAnyAddress | None, dialect: Dialect) -> str | None:
        return str(value) if value else None

    def process_result_value(self, value: str | None, dialect: Dialect) -> IPvAnyAddress | None:
        if value is None:
            return None
        return ip_address(value)

    def process_literal_param(self, value: str | None, dialect: Dialect) -> str:
        raise NotImplementedError("Not yet implemented")


class PgCIDR(TypeDecorator):
    """
    A codec for :py:mod:`ipaddress` IP networks.
    """

    impl = CIDR

    def process_bind_param(self, value: IPvAnyNetwork | str | None, dialect: Dialect) -> str | None:
        if value is None:
            return None

        if isinstance(value, str):
            value = ip_network(value)

        if not isinstance(value, (IPv4Network | IPv6Network)):
            msg = "PgCIDR field values must be of type ip_network! " f"You gave me {value!r}"
            raise TypeError(msg)

        return str(value) if value else None

    def process_result_value(self, value: str | None, dialect: Dialect) -> IPvAnyNetwork | None:
        if value is None:
            return None

        return ip_network(value)

    def process_literal_param(self, value: str | None, dialect: Dialect) -> str:
        raise NotImplementedError("Not yet implemented")


uuid_pk = Annotated[uuid.UUID, mapped_column(UUID(as_uuid=True), default=uuid.uuid4, primary_key=True)]
int_pk = Annotated[int, mapped_column(Integer, primary_key=True)]
bool_true = Annotated[bool, mapped_column(Boolean, server_default=expression.true())]
bool_false = Annotated[bool, mapped_column(Boolean, server_default=expression.false())]
datetime_required = Annotated[datetime, mapped_column(DateTime(timezone=True))]
datetime_required = Annotated[datetime, mapped_column(DateTime(timezone=True))]
date_required = Annotated[date, mapped_column(Date)]
date_optional = Annotated[date | None, mapped_column(Date)]
i18n_name = Annotated[VisibleName, mapped_column(MutableDict.as_mutable(HSTORE), unique=True)]
