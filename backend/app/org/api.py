from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app._types import IdResponse, ListT
from app.db import SiteGroup, User
from app.deps import auth, get_session
from app.org import schemas, services
from app.utils.cbv import cbv

router = APIRouter()


@cbv(router)
class SiteGroupAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    dto = services.SiteGroupDto(SiteGroup)

    @router.post("/site-groups", operation_id="4c6595c8-1aa1-4613-b128-37e7bca87e28")
    async def create_site_group(self, site_group: schemas.SiteGroupCreate) -> IdResponse:
        new_group = await self.dto.create(self.session, site_group)
        return IdResponse(id=new_group.id)

    @router.put("site-groups/{id}", operation_id="f85e5555-546d-44a3-8f39-44ef62de8d87")
    async def update_site_group(self, id: int, site_group: schemas.SiteGroupUpdate) -> IdResponse:
        db_group = await self.dto.get_one_or_404(self.session, id)
        await self.dto.update(self.session, db_group, site_group)
        return IdResponse(id=id)

    @router.get("/site-groups/{id}", operation_id="9c4e0278-7547-43a1-98ef-5703f7c1ea90")
    async def get_site_group(self, id: int) -> schemas.SiteGroup:
        db_group = await self.dto.get_one_or_404(self.session, id)
        return schemas.SiteGroup.model_validate(db_group)

    @router.get("/groups", operation_id="150588da-6075-408c-8d63-9661e8fcd097")
    async def get_groups(self, q: schemas.SiteGroupQuery = Depends()) -> ListT[schemas.SiteGroupList]:
        count, results = await self.dto.list_and_count(self.session, q)
        return ListT(count=count, results=[schemas.SiteGroupList.model_validate(r) for r in results])

    @router.delete("/groups/{id}", operation_id="506e84a1-5256-420d-bae1-7bb1f1676175")
    async def delete_groups(self, id: int) -> IdResponse:
        db_group = await self.dto.get_one_or_404(self.session, id)
        await self.dto.delete(self.session, db_group)
        return IdResponse(id=id)
