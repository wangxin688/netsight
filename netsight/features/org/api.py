from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from netsight.core.utils.cbv import cbv
from netsight.core.utils.validators import list_to_tree
from netsight.features._types import AuditLog, IdResponse, ListT
from netsight.features.admin.models import User
from netsight.features.deps import auth, get_session
from netsight.features.org import schemas, services
from netsight.features.org.models import Location, Site, SiteGroup

router = APIRouter()


@cbv(router)
class SiteGroupAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    service = services.site_group_service

    @router.post("/site-groups", operation_id="4c6595c8-1aa1-4613-b128-37e7bca87e28")
    async def create_site_group(self, site_group: schemas.SiteGroupCreate) -> IdResponse:
        new_group = await self.service.create(self.session, site_group)
        return IdResponse(id=new_group.id)

    @router.put("/site-groups/{id}", operation_id="f85e5555-546d-44a3-8f39-44ef62de8d87")
    async def update_site_group(self, id: int, site_group: schemas.SiteGroupUpdate) -> IdResponse:
        db_group = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_group, site_group)
        return IdResponse(id=id)

    @router.get("/site-groups/{id}", operation_id="9c4e0278-7547-43a1-98ef-5703f7c1ea90")
    async def get_site_group(self, id: int) -> schemas.SiteGroup:
        db_group = await self.service.get_one_or_404(
            self.session,
            id,
            selectinload(SiteGroup.created_by).load_only(User.id, User.name, User.email, User.avatar),
            selectinload(SiteGroup.updated_by).load_only(User.id, User.name, User.email, User.avatar),
        )
        return schemas.SiteGroup.model_validate(db_group)

    @router.get("/site-groups", operation_id="150588da-6075-408c-8d63-9661e8fcd097")
    async def get_site_groups(self, q: schemas.SiteGroupQuery = Depends()) -> ListT[schemas.SiteGroupList]:
        count, results = await self.service.list_and_count(
            self.session,
            q,
            selectinload(SiteGroup.created_by).load_only(User.id, User.name, User.email, User.avatar),
            selectinload(SiteGroup.updated_by).load_only(User.id, User.name, User.email, User.avatar),
        )
        return ListT(count=count, results=[schemas.SiteGroupList.model_validate(r) for r in results])

    @router.delete("/site-groups/{id}", operation_id="506e84a1-5256-420d-bae1-7bb1f1676175")
    async def delete_site_groups(self, id: int) -> IdResponse:
        db_group = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_group)
        return IdResponse(id=id)


@cbv(router)
class SiteAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    service = services.site_service

    @router.post("/sites", operation_id="3126a8cb-0e8b-44b4-80ab-25458a838a14")
    async def create_site(self, site: schemas.SiteCreate) -> IdResponse:
        new_site = await self.service.create(self.session, site)
        return IdResponse(id=new_site.id)

    @router.put("/sites/{id}", operation_id="b1497fbc-5675-470a-9cfb-c829860b3a3d")
    async def update_site(self, id: int, site: schemas.SiteUpdate) -> IdResponse:
        db_site = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_site, site)
        return IdResponse(id=id)

    @router.get("/sites/{id}", operation_id="d3bae13a-55fc-49c1-8665-339d51292e09")
    async def get_site(self, id: int) -> schemas.Site:
        db_site = await self.service.get_one_or_404(
            self.session,
            id,
            selectinload(SiteGroup.created_by).load_only(User.id, User.name, User.email, User.avatar),
            selectinload(SiteGroup.updated_by).load_only(User.id, User.name, User.email, User.avatar),
            selectinload(Site.site_group).load_only(SiteGroup.id, SiteGroup.name),
            selectinload(Site.network_contact).load_only(User.id, User.name, User.email, User.avatar),
            selectinload(Site.it_contact).load_only(User.id, User.name, User.email, User.avatar),
        )
        return schemas.Site.model_validate(db_site)

    @router.get("/sites", operation_id="8528d436-f475-4dfb-9a35-f408fac650ff")
    async def get_sites(self, q: schemas.SiteQuery = Depends()) -> ListT[schemas.Site]:
        count, results = await self.service.list_and_count(
            self.session,
            q,
            selectinload(SiteGroup.created_by).load_only(User.id, User.name, User.email, User.avatar),
            selectinload(SiteGroup.updated_by).load_only(User.id, User.name, User.email, User.avatar),
            selectinload(Site.site_group).load_only(SiteGroup.id, SiteGroup.name),
            selectinload(Site.network_contact).load_only(User.id, User.name, User.email, User.avatar),
            selectinload(Site.it_contact).load_only(User.id, User.name, User.email, User.avatar),
        )
        return ListT(count=count, results=[schemas.Site.model_validate(r) for r in results])

    @router.delete("/sites/{id}", operation_id="1b349641-8fd1-42aa-b206-a6bb1bfa7de1")
    async def delete_sites(self, id: int) -> IdResponse:
        db_group = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_group)
        return IdResponse(id=id)

    @router.get("/sites/{id}/auditlogs", operation_id="3927c00d-108c-46b2-88f3-1f27984b95a0")
    async def get_site_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.service.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])

    @router.get("/sites/{id}/locations", operation_id="6062a33d-e699-42b8-a775-1b48f6a30209")
    async def get_site_locations(self, id: int) -> schemas.LocationTree:
        locations = await self.service.get_site_locations(self.session, id)
        tree = list_to_tree([location.dict() for location in locations])
        return schemas.LocationTree.model_validate(tree)


class LocationAPI:
    session: AsyncSession = Depends(get_session)
    user: User = Depends(auth)
    service = services.location_service

    @router.post("/locations", operation_id="0ffd1157-d326-49b8-a470-07027c962fed")
    async def create_location(self, location: schemas.LocationCreate) -> IdResponse:
        new_location = await self.service.create(self.session, location)
        return IdResponse(id=new_location.id)

    @router.put("/locations/{id}", operation_id="bb6d3b19-70fc-4501-add1-cc6f8376dd49")
    async def update_location(self, id: int, location: schemas.LocationUpdate) -> IdResponse:
        db_location = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_location, location)
        return IdResponse(id=id)

    @router.get("/locations/{id}", operation_id="740bbfd7-673e-4c66-884f-f1d83f43c946")
    async def get_location(self, id: int) -> schemas.Location:
        db_location = await self.service.get_one_or_404(
            self.session,
            id,
            selectinload(Location.site).load_only(Site.id, Site.name, Site.site_code),
            selectinload(Location.created_by).load_only(User.id, User.name, User.email, User.avatar),
            selectinload(Location.updated_by).load_only(User.id, User.name, User.email, User.avatar),
        )
        return schemas.Location.model_validate(db_location)

    @router.delete("/locations/{id}", operation_id="7bf1bc42-4f89-4333-af8c-053977e91f27")
    async def delete_locations(self, id: int) -> IdResponse:
        db_location = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_location)
        return IdResponse(id=id)

    @router.get("/locations/{id}/auditlogs", operation_id="c665ca89-4eb3-4446-9770-0fe650887d56")
    async def get_location_auditlogs(self, id: int) -> ListT[AuditLog]:
        count, results = await self.service.get_audit_log(self.session, id)
        if not results:
            return ListT(count=0, results=None)
        return ListT(count=count, results=[AuditLog.model_validate(r) for r in results])
