from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm import selectinload

from src.api.auth.models import User
from src.api.base import BaseResponse
from src.api.dcim import schemas
from src.api.dcim.models import Site
from src.api.deps import audit_without_data, get_current_user, get_session
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_0, ERR_NUM_4004

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class SiteCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    audit = Depends(audit_without_data)

    @router.get("/sites/{id}")
    async def get_site(self, id: int) -> BaseResponse:
        result: AsyncResult = await self.session.execute(
            select(Site)
            .where(Site.id == id)
            .options(
                selectinload(
                    Site.dcim_device,
                    Site.dcim_location,
                    Site.dcim_rack,
                    Site.circuit_termination,
                )
            )
        )
        local_site: Site | None = result.scalars().first()
        if not local_site:
            return_info = ERR_NUM_4004
            return_info.msg = f"Site #{id} not found,  requested data not existed"
            return return_info
        return_info = ERR_NUM_0
        return_info.data = local_site
        return return_info

    @router.get("/sites")
    async def get_sites(self, site: schemas.SiteQuery):
        pass
