from enum import IntEnum

from src._types import AppStrEnum


class Env(IntEnum):
    PRD = 0
    DEV = 1


class ReservedRoleSlug(AppStrEnum):
    ADMIN = "admin"


class SiteStatus(AppStrEnum):
    PLANNING = 1
    VALIDAING = 2
    ACTIVE = 3
    RETIRED = 4


class SiteClassfication(AppStrEnum):
    DATACENTER = "DataCenter"
    CAMPUS = "Campus"
    OFFICE = "Office"


class EntityPhysicalClass(IntEnum):
    other = 1
    unknown = 2
    chassis = 3
    backplane = 4
    container = 5
    powerSupply = 6  # noqa: N815
    fan = 7
    sensor = 8
    module = 9
    port = 10
    stack = 11
    cpu = 12


class IPPrefixStatus(IntEnum):
    Active = 1
    Reserved = 2
    Deprecated = 3


class IPVersion(IntEnum):
    IPv4 = 4
    IPv6 = 6


class IPAddressStatus(IntEnum):
    Active = 1
    Reserved = 2
    Deprecated = 3
    DHCP = 4
    Available = 5


class VLANStatus(IntEnum):
    Active = 1
    Reserved = 2
    Deprecated = 3


class CircuitStatus(IntEnum):
    Planning = 1
    Active = 2
    Provisioning = 3
    Offline = 4
