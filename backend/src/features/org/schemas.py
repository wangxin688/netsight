from fastapi import Query
from pydantic import Field, model_validator

from src.features import schemas
from src.features._types import (
    AuditUser,
    AuthUserBase,
    BaseModel,
    NameChineseStr,
    NameStr,
    QueryParams,
)
from src.features.consts import LocationStatus, LocationType, SiteStatus


class SiteGroupBase(BaseModel):
    name: str
    description: str | None = None


class SiteGroupCreate(SiteGroupBase):
    name: NameChineseStr
    site: list[int]


class SiteGroupUpdate(SiteGroupCreate):
    name: NameChineseStr | None = None
    site: list[int] | None = None


class SiteGroupQuery(QueryParams):
    name: list[NameChineseStr] | None = Field(Query(default=[]))


class SiteGroup(SiteGroupBase, AuditUser):
    id: int
    site: list[schemas.SiteBrief] | None = None


class SiteGroupList(SiteGroupBase, AuditUser):
    id: int
    site_count: int


class SiteBase(BaseModel):
    name: str
    site_code: str
    status: SiteStatus
    facility_code: str | None = None
    time_zone: int | None = None
    country: str | None = Field(default=None, description="ISO 3166-1 alpha-2 code, timezone will be automatically set")
    city: str | None = None
    address: str
    latitude: float
    longitude: float
    classfication: str | None = None
    comments: str | None


class SiteCreate(SiteBase):
    name: NameChineseStr
    site_code: NameStr
    site_group_id: int | None = None
    asn: list[int] | None = None
    it_contact_id: int | None = None
    network_contact_id: int | None = None


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
    time_zone: list[int] | None = Field(Query(default=[]))
    classification: list[int] | None = Field(Query(default=[]))
    it_contact_id: list[int] | None = Field(Query(default=[]))
    network_contact_id: list[int] | None = Field(Query(default=[]))


class Site(SiteBase, AuditUser):
    id: int
    asn: list[schemas.ASNBrief] | None = None
    it_contact: AuthUserBase | None = None
    network_contact: AuthUserBase | None = None
    site_group: schemas.SiteGroupBrief | None = None
    device_count: int
    circuit_count: int


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


class LocationUpdate(LocationBase):
    name: NameChineseStr | None = None
    location_type: LocationType | None = None
    status: LocationStatus | None = None
    parent_id: int | None = None


class LocationQuery(QueryParams):
    name: list[NameChineseStr] | None = Field(Query(default=[]))
    location_type: list[LocationType] | None = Field(Query(default=[]))
    status: list[LocationStatus] | None = Field(Query(default=[]))
    site_id: list[int] | None = Field(Query(default=[]))
    parent_id: list[int] | None = Field(Query(default=[]))


class LocationTree(LocationBase):
    id: int
    children: list["LocationTree"] | None = None


class Location(LocationBase, AuditUser):
    id: int
    site: schemas.SiteBrief
