from ipaddress import IPv4Network, IPv6Network, ip_address, ip_interface, ip_network

from sqlalchemy import Dialect
from sqlalchemy.dialects.postgresql import CIDR, INET
from sqlalchemy.types import TypeDecorator

from netsight.features._types import IPvAnyAddress, IPvAnyInterface, IPvAnyNetwork


class PgIpInterface(TypeDecorator):
    """
    A codec for :py:mod:`ipaddress` interfaces.
    """

    impl = INET

    def process_bind_param(self, value: IPvAnyInterface | None, dialect: Dialect) -> str | None:  # noqa: ARG002
        return str(value) if value else None

    def process_result_value(self, value: IPvAnyInterface | None, dialect: Dialect) -> IPvAnyInterface | None:  # noqa: ARG002
        return ip_interface(value) if value else None

    def process_literal_param(self, value: str | None, dialect: Dialect) -> str:
        raise NotImplementedError("Not yet implemented")


class PgIpAddress(TypeDecorator):
    """
    A codec for :py:mod:`ipaddress` IP addresses.
    """

    impl = INET

    def process_bind_param(self, value: IPvAnyAddress | None, dialect: Dialect) -> str | None:  # noqa: ARG002
        return str(value) if value else None

    def process_result_value(self, value: str | None, dialect: Dialect) -> IPvAnyAddress | None:  # noqa: ARG002
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

    def process_bind_param(self, value: IPvAnyNetwork | str | None, dialect: Dialect) -> str | None:  # noqa: ARG002
        if value is None:
            return None

        if isinstance(value, str):
            value = ip_network(value)

        if not isinstance(value, (IPv4Network | IPv6Network)):
            msg = "PgCIDR field values must be of type ip_network! " f"You gave me {value!r}"
            raise TypeError(msg)

        return str(value) if value else None

    def process_result_value(self, value: str | None, dialect: Dialect) -> IPvAnyNetwork | None:  # noqa: ARG002
        if value is None:
            return None

        return ip_network(value)

    def process_literal_param(self, value: str | None, dialect: Dialect) -> str:
        raise NotImplementedError("Not yet implemented")
