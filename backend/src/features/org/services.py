from typing import TYPE_CHECKING

from src.core.errors.err_codes import ERR_20001
from src.core.errors.exceptions import GenerError
from src.core.repositories import BaseRepository
from src.features.org import schemas
from src.features.org.models import Contact, ContactRole, Location, Site, SiteGroup

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class SiteGroupDto(
    BaseRepository[SiteGroup, schemas.SiteGroupCreate, schemas.SiteGroupUpdate, schemas.SiteGroupQuery]
): ...


class SiteDto(BaseRepository[Site, schemas.SiteCreate, schemas.SiteUpdate, schemas.SiteQuery]): ...


class LocationDto(BaseRepository[Location, schemas.LocationCreate, schemas.LocationUpdate, schemas.LocationQuery]):
    async def location_compatible(self, session: "AsyncSession", location_id: int, site_id: int) -> None:
        db_location = await self.get_one_or_404(session, location_id)
        if db_location.site_id != site_id:
            raise GenerError(ERR_20001)


class ContactRoleDto(
    BaseRepository[ContactRole, schemas.ContactRoleCreate, schemas.ContactRoleUpdate, schemas.ContactRoleQuery]
): ...


class ContactDto(BaseRepository[Contact, schemas.ContactCreate, schemas.ContactUpdate, schemas.ContactQuery]): ...
