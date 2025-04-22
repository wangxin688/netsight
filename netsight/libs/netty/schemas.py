from typing import TypedDict


class Interface(TypedDict):
    if_index: int
    if_name: str
    if_alias: str
    if_type: str
    if_mtu: int
    if_speed: int  # physical speed
    if_duplex: str
    if_admin_status: int
