from enum import StrEnum


class NetmikoDriver(StrEnum):
    IOS = "cisco_ios"
    NXOS = "cisco_nxos"
    IOSXR = "cisco_xr"
    IOSXE = "cisco_xe"
    HUAWEI = "huawei"
    HUAWEI_VRP = "huawei_vrp"
    HUAWEI_VRPV8 = "huawei_vrp_v8"
    HP_COMWARE = "hp_comware"
    ARUBA = "aruba_os"


PING_SOURCE = ""
PING_SOURCE_INTERFACE = ""
PING_TTL = 255
PING_TIMEOUT = 2
PING_SIZE = 100
PING_COUNT = 5
PING_VRF = ""
