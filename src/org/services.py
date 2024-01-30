from typing import TYPE_CHECKING

from src.db.dtobase import DtoBase
from src.errors import ERR_20001
from src.exceptions import GenerError
from src.org import schemas
from src.org.models import Contact, ContactRole, Location, Site, SiteGroup

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession

__all__ = ("SiteGroupDto", "SiteDto", "LocationDto", "ContactRoleDto", "ContactDto")


class SiteGroupDto(DtoBase[SiteGroup, schemas.SiteGroupCreate, schemas.SiteGroupUpdate, schemas.SiteGroupQuery]):
    ...


class SiteDto(DtoBase[Site, schemas.SiteCreate, schemas.SiteUpdate, schemas.SiteQuery]):
    ...


class LocationDto(DtoBase[Location, schemas.LocationCreate, schemas.LocationUpdate, schemas.LocationQuery]):
    async def location_compatible(self, session: "AsyncSession", location_id: int, site_id: int) -> None:
        db_location = await self.get_one_or_404(session, location_id)
        if db_location.site_id != site_id:
            raise GenerError(ERR_20001)


class ContactRoleDto(
    DtoBase[ContactRole, schemas.ContactRoleCreate, schemas.ContactRoleUpdate, schemas.ContactRoleQuery]
):
    ...


class ContactDto(DtoBase[Contact, schemas.ContactCreate, schemas.ContactUpdate, schemas.ContactQuery]):
    ...
