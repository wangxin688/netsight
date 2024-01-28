from fastapi import Query
from pydantic import EmailStr, Field, model_validator
from pydantic_extra_types.phone_numbers import PhoneNumber

from src._types import (
    AuditTime,
    BaseModel,
    IdCreate,
    NameChineseStr,
    NameStr,
    QueryParams,
)
from src.consts import LocationStatus, LocationType, SiteStatus
from src.internal import schemas


class SiteGroupBase(BaseModel):
    name: str
    slug: str
    description: str | None = None


class SiteGroupCreate(SiteGroupBase):
    name: NameChineseStr
    slug: NameStr
    site: list[IdCreate]


class SiteGroupUpdate(SiteGroupCreate):
    name: NameChineseStr | None = None
    slug: NameStr | None = None
    site: list[IdCreate] | None = None


class SiteGroupQuery(QueryParams):
    name: list[NameChineseStr] | None = Field(Query(default=[]))
    slug: list[NameStr] | None = Field(Query(default=[]))


class SiteGroup(SiteGroupBase, AuditTime):
    id: int
    site: list[schemas.SiteBrief] | None = None


class SiteGroupList(SiteGroupBase, AuditTime):
    id: int
    site_count: int


class SiteBase(BaseModel):
    name: str
    site_code: str
    status: SiteStatus
    facility_code: str | None = None
    time_zone: str | None = None
    country: str | None = None
    city: str | None = None
    address: str
    latitude: float
    longitude: float
    classfication: str | None = None
    comments: str | None


class SiteContactCreate(BaseModel):
    contact_id: int
    role_id: int


class SiteCreate(SiteBase):
    name: NameChineseStr
    site_code: NameStr
    site_group_id: int | None = None
    asn: list[IdCreate] | None = None
    site_contact: list[SiteContactCreate] | None = None


class SiteUpdate(SiteCreate):
    name: NameChineseStr | None = None
    site_code: NameStr | None = None
    status: SiteStatus | None = None
    address: str | None = None
    latitude: float | None = None
    longitude: float | None = None


class SiteQuery(QueryParams):
    name: list[NameChineseStr] | None = Field(Query(default=[]))
    site_code: list[NameStr] | None = Field(Query(default=[]))
    status: list[SiteStatus] | None = Field(Query(default=[]))
    site_group_id: list[int] | None = Field(Query(default=[]))
    country: list[str] | None = Field(Query(default=[]))
    city: list[str] | None = Field(Query(default=[]))
    time_zone: list[str] | None = Field(Query(default=[]))
    classification: list[int] | None = Field(Query(default=[]))


class Site(SiteBase):
    id: int
    asn: list[schemas.ASNBrief] | None = None
    site_contact: list["SiteContact"] | None = None
    site_group: list[schemas.SiteGroupBrief] | None = None
    device_count: int
    circuit_count: int
    ap_count: int
    prefix_count: int
    rack_count: int
    vlan_count: int


class LocationBase(BaseModel):
    name: str
    location_type: LocationType
    status: LocationStatus
    description: str | None = None


class LocationCreate(LocationBase):
    name: NameChineseStr
    parent_id: int | None = None
    site_id: int

    @model_validator(mode="after")
    def check_parent_id(self):
        if self.location_type == LocationType.Building and self.parent_id:
            raise ValueError("parent_id should be None when location_type is Building")
        return self


class LocationUpdate(LocationCreate):
    name: NameChineseStr | None = None
    location_type: LocationType | None = None
    status: LocationStatus | None = None
    site_id: int | None = None


class LocationQuery(QueryParams):
    name: list[NameChineseStr] | None = Field(Query(default=[]))
    location_type: list[LocationType] | None = Field(Query(default=[]))
    status: list[LocationStatus] | None = Field(Query(default=[]))
    site_id: list[int] | None = Field(Query(default=[]))
    parent_id: list[int] | None = Field(Query(default=[]))


class Location(LocationBase, AuditTime):
    id: int
    site: schemas.SiteBrief
    children: list["Location"] | None = None


class ContactBase(BaseModel):
    name: str
    avatar: str | None = None
    email: str | None = None
    phone: str | None = None


class ContactCreate(ContactBase):
    name: NameChineseStr
    email: EmailStr | None = None
    phone: PhoneNumber | None = None

    @model_validator(mode="after")
    def check_email(self):
        if not self.email or not self.phone:
            raise ValueError("Email or phone should not be provided any one of it.")
        return self


class ContactUpdate(ContactBase):
    name: NameChineseStr | None = None
    email: EmailStr | None = None
    phone: PhoneNumber | None = None


class ContactQuery(QueryParams):
    name: list[NameChineseStr] | None = Field(Query(default=[]))
    email: list[EmailStr] | None = Field(Query(default=[]))
    phone: list[PhoneNumber] | None = Field(Query(default=[]))


class Contact(ContactBase):
    id: int


class SiteContact(ContactBase):
    contact_role: schemas.ContactRoleBrief


class ContactRoleBase(BaseModel):
    name: str
    description: str | None = None


class ContactRoleCreate(ContactRoleBase):
    name: NameChineseStr


class ContactRoleUpdate(ContactRoleCreate):
    name: NameChineseStr | None = None


class ContactRole(ContactRoleBase):
    id: int

class ContactRoleQuery(QueryParams):
    name: list[NameChineseStr] | None = Field(Query(default=[]))


class CircuitContact(ContactBase):
    contact_role: schemas.ContactRoleBrief
