from pydantic import IPvAnyAddress, IPvAnyNetwork

from netsight.features._types import BaseModel, I18nField


## ------Circuit---------
class ISPBrief(BaseModel):
    id: int
    name: I18nField


class CircuitBrief(BaseModel):
    id: int
    name: str


## ------IPAM-------------
class ASNBrief(BaseModel):
    id: int
    asn: int


class BlockBrief(BaseModel):
    id: int
    block: IPvAnyNetwork


class PrefixBrief(BaseModel):
    id: int
    prefix: IPvAnyNetwork


class IPAddressBrief(BaseModel):
    id: int
    address: IPvAnyAddress


class IPRangeBrief(BaseModel):
    id: int
    start_address: IPvAnyAddress
    end_address: IPvAnyAddress


class VLANBrief(BaseModel):
    id: int
    name: str
    vid: int


class VRFBrief(BaseModel):
    id: int
    name: str
    rd: str


class RouteTargetBrief(BaseModel):
    id: int
    name: str


## -------DCIM----------
class DeviceBrief(BaseModel):
    id: int
    name: str
    management_ip: IPvAnyAddress


class InterfaceBrief(BaseModel):
    id: int
    name: str
    description: str | None = None


class InterfaceToDevice(InterfaceBrief):
    device: DeviceBrief


class ManufacturerBrief(BaseModel):
    id: int
    name: I18nField


class DeviceTypeBrief(BaseModel):
    id: int
    name: str


class PlatformBrief(BaseModel):
    id: int
    name: str
    netmiko_driver: str


## -------ORG-----------
class SiteGroupBrief(BaseModel):
    id: int
    name: str


class SiteBrief(BaseModel):
    id: int
    name: str
    site_code: str


class LocationBrief(BaseModel):
    id: int
    name: str


class ContactRoleBrief(BaseModel):
    id: int
    name: str


## -------WLAN----------
## -------AUTH----------
## -------ARCH----------
class CircuitTypeBrief(BaseModel):
    id: int
    name: I18nField


class DeviceRoleBrief(BaseModel):
    id: int
    name: I18nField


class IPRoleBrief(BaseModel):
    id: int
    name: I18nField


## -------SERVER----------
