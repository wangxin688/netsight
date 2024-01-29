from src.db.dtobase import DtoBase
from src.org import schemas
from src.org.models import Contact, ContactRole, Location, Site, SiteGroup


class SiteGroupDto(DtoBase[SiteGroup, schemas.SiteGroupCreate, schemas.SiteGroupUpdate, schemas.SiteGroupQuery]):
    ...


class SiteDto(DtoBase[Site, schemas.SiteCreate, schemas.SiteUpdate, schemas.SiteQuery]):
    ...


class LocationDto(DtoBase[Location, schemas.LocationCreate, schemas.LocationUpdate, schemas.LocationQuery]):
    ...


class ContactRoleDto(
    DtoBase[ContactRole, schemas.ContactRoleCreate, schemas.ContactRoleUpdate, schemas.ContactRoleQuery]
):
    ...


class ContactDto(DtoBase[Contact, schemas.ContactCreate, schemas.ContactUpdate, schemas.ContactQuery]):
    ...
