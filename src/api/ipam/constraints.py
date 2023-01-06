from typing import Literal

IPADDRESS_STATUS = Literal["Active", "Reserved", "Deprecated", "DHCP", "Available"]
VLAN_STATUS = Literal["Active", "Reserved", "Deprecated"]
IP_VERSION = Literal["IPv4", "IPv6"]
IP_STATUS = Literal["Active", "Reserved", "Deprecated", "DHCP", "Available"]


BGP_ASN_MIN = 1
BGP_ASN_MAX = 2**32 - 1

VRF_RD_MAX_LENGTH = 21

PREFIX_MIN_LENGTH = 1
PREFIX_MAX_LENGTH = 127

IPADDRESS_MASK_MIN_LENGTH = 1
IPADDRESS_MASK_MAX_LENGTH = 128

VLAN_VID_MIN = 1
VLAN_VID_MAX = 4094

VXLAN_VID_MIN = 1
VXLAN_VID_MAX = 2 * 24 - 1
