from enum import IntEnum, StrEnum


class Env(IntEnum):
    PRD = 0
    DEV = 1


class ReservedRoleSlug(StrEnum):
    ADMIN = "admin"


class SiteStatus(StrEnum):
    Planning = "Planning"
    Deploying = "Deploying"
    Vlidating = "Validating"
    Active = "Active"
    Retired = "Retired"


class LocationType(StrEnum):
    Building = "Building"
    Floor = "Floor"
    ServerRoom = "ServerRoom"


class LocationStatus(StrEnum):
    Planning = "Planning"
    Vlidating = "Validating"
    Active = "Active"
    Retired = "Retired"


class DeviceStatus(StrEnum):
    Active = "Active"
    Offline = "Offline"
    Staged = "Staged"
    Inventory = "Inventory"
    Scrapped = "Scrapped"


class DeviceEquipmentType(StrEnum):
    Power = "Power"
    Fan = "Fan"
    SFP = "SFP"


class DeviceConfigChangeType(StrEnum):
    Manual = "Manual"
    Event = "Event"


class APMode(StrEnum):
    Fix = "Fix"
    Fat = "Fat"


class InterfaceAdminStatus(StrEnum):
    Disabled = "Disabled"
    Enabled = "Enabled"


class PrefixStatus(StrEnum):
    Available = "Available"
    Reserved = "Reserved"
    Deprecated = "Deprecated"


class IPRangeStatus(StrEnum):
    Available = "Available"
    Reserved = "Reserved"
    Deprecated = "Deprecated"


class SiteClassfication(StrEnum):
    DATACENTER = "DataCenter"
    CAMPUS = "Campus"
    OFFICE = "Office"


class EntityPhysicalClass(StrEnum):
    other = "other"
    unknown = "unknown"
    chassis = "chassis"
    backplane = "backplane"
    container = "container"
    powerSupply = "powerSupply"  # noqa: N815
    fan = "fan"
    sensor = "sensor"
    module = "module"
    port = "port"
    stack = "stack"
    cpu = "cpu"


class IPVersion(IntEnum):
    IPv4 = 4
    IPv6 = 6


class IPAddressStatus(StrEnum):
    Active = "Active"
    Reserved = "Reserved"
    Deprecated = "Deprecated"
    DHCP = "DHCP"
    Available = "Available"


class VLANStatus(StrEnum):
    Active = "Active"
    Reserved = "Reserved"
    Deprecated = "Deprecated"


class CircuitStatus(StrEnum):
    Planning = "Planning"
    Active = "Active"
    Provisioning = "Provisioning"
    Offline = "Offline"


class CircuitType(StrEnum):
    INTERNET = "INTERNET"
    P2P = "P2P"
    IEPL = "IEPL"
    DPLC = "DPLC"
    ADSL = "ADSL"
    MPLS = "MPLS"
    BGP = "BGP"
