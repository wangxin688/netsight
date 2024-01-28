from collections.abc import Sequence

from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth import schemas
from src.org.models import SiteGroup, Site, Location, ContactRole, Contact
from src.org import schemas
from src.context import locale_ctx
from src.db.dtobase import DtoBase
from src.exceptions import NotFoundError, PermissionDenyError
from src.security import verify_password

class SiteGroupDto(DtoBase[SiteGroup, schemas.SiteGroupCreate, schemas.SiteGroupUpdate, schemas.SiteGroupQuery]):
    ...

class SiteDto(DtoBase[Site, schemas.SiteCreate, schemas.SiteUpdate, schemas.SiteQuery]):
    ...

class LocationDto(DtoBase[Location, schemas.LocationCreate, schemas.LocationUpdate, schemas.LocationQuery]):
    ...

class ContactRoleDto(DtoBase[ContactRole, schemas.ContactRoleCreate, schemas.ContactRoleUpdate, schemas.ContactRoleQuery]):
    ...

class ContactDto(DtoBase[Contact, schemas.ContactCreate, schemas.ContactUpdate, schemas.ContactQuery]):
    ...