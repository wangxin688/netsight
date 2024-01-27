from enum import Enum, IntEnum

from src._types import AppStrEnum


class Env(IntEnum):
    PRD = 0
    DEV = 1


class ReservedRoleSlug(AppStrEnum):
    ADMIN = "admin"


class SiteStatus(IntEnum):
    Planning = 1
    Vlidating = 2
    Active = 3
    Retired = 4


class LocationStatus(IntEnum):
    Planning = 1
    Vlidating = 2
    Active = 3
    Retired = 4


class DeviceStatus(IntEnum):
    Active = 1
    Offline = 2
    Staged = 3
    Inventory = 4


class RackStatus(IntEnum):
    Active = 1
    Offline = 2
    Reserved = 3


class InterfaceAdminStatus(IntEnum):
    Disabled = 0
    Enabled = 1


class PrefixStatus(IntEnum):
    Available = 1
    Reserved = 2
    Deprecated = 3


class IPRangeStatus(IntEnum):
    Available = 1
    Reserved = 2
    Deprecated = 3


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


class CircuitType(str, Enum):
    INTERNET = "INTERNET"
    P2P = "P2P"
    IEPL = "IEPL"
    DPLC = "DPLC"
    ADSL = "ADSL"
    MPLS = "MPLS"
    BGP = "BGP"
