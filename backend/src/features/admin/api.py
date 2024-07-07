from uuid import UUID

from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.core.config import settings
from src.core.errors.err_codes import ERR_10005
from src.core.errors.exception_handlers import GenerError
from src.core.utils.cbv import cbv
from src.core.utils.validators import list_to_tree
from src.features._types import IdResponse, ListT
from src.features.admin import schemas, services
from src.features.admin.models import Group, Permission, Role, User
from src.features.admin.security import generate_access_token_response
from src.features.deps import auth, get_session

router = APIRouter()


@router.post("/pwd-login", operation_id="c5f719b1-7adf-4b4e-a498-732b8da7d758")
async def login_pwd(
    user: OAuth2PasswordRequestForm = Depends(),
    session: AsyncSession = Depends(get_session),
) -> schemas.AccessToken:
    result = await services.user_service.verify_user(session, user)
    return generate_access_token_response(result.id)


@cbv(router)
class UserAPI:
    user: User = Depends(auth)
    session: AsyncSession = Depends(get_session)
    service = services.user_service

    @router.post("/users", operation_id="5091fff6-1adc-4a22-8a8c-ef0107122df7", summary="创建新用户/Create new user")
    async def create_user(self, user: schemas.UserCreate) -> IdResponse:
        new_user = await self.service.create(self.session, user)
        result = await self.service.commit(self.session, new_user)
        return IdResponse(id=result.id)

    @router.get(
        "/users/{id}",
        operation_id="276a8c69-2f5c-40d5-91c4-d0ddd1c24766",
        summary="获取单个用户/Get user information by ID",
    )
    async def get_user(self, id: int) -> schemas.User:
        db_user = await self.service.get_one_or_404(
            self.session,
            id,
            selectinload(User.role).load_only(Role.id, Role.name),
            selectinload(User.group).load_only(Group.id, Group.name),
        )
        return schemas.User.model_validate(db_user)

    @router.get("/users", operation_id="2485e2a2-4d81-4601-a6fd-c633b23ce5fc")
    async def get_users(self, query: schemas.UserQuery = Depends()) -> ListT[schemas.User]:
        count, results = await self.service.list_and_count(
            self.session,
            query,
            selectinload(User.role).load_only(Role.id, Role.name),
            selectinload(User.group).load_only(Group.id, Group.name),
        )
        return ListT(count=count, results=[schemas.User.model_validate(r) for r in results])

    @router.put("/users/{id}", operation_id="ea0078b9-7f16-4b55-9264-fa7ba48737a9")
    async def update_user(self, id: int, user: schemas.UserUpdate) -> IdResponse:
        update_user = user.model_dump(exclude_unset=True)
        if "password" in update_user and update_user["password"] is None:
            raise GenerError(ERR_10005, status_code=status.HTTP_406_NOT_ACCEPTABLE)
        db_user = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_user, user)
        return IdResponse(id=id)

    @router.delete("/users/{id}", operation_id="78e48ceb-d7cf-46fe-bf9e-d04958aade7d")
    async def delete_user(self, id: int) -> IdResponse:
        db_user = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_user)
        return IdResponse(id=id)


@cbv(router)
class GroupAPI:
    user: User = Depends(auth)
    session: AsyncSession = Depends(get_session)
    service = services.group_service

    @router.post("/groups", operation_id="9e3e639d-c694-467d-9209-717b038cf267")
    async def create_group(self, group: schemas.GroupCreate) -> IdResponse:
        new_group = await self.service.create(self.session, group)
        return IdResponse(id=new_group.id)

    @router.get("/groups/{id}", operation_id="00327087-9443-4d24-8d04-e396e3244744")
    async def get_group(self, id: int) -> schemas.Group:
        db_group = await self.service.get_one_or_404(self.session, id, undefer_load=True)
        return schemas.Group.model_validate(db_group)

    @router.get("/groups", operation_id="a1d1f8f1-4d4d-4fab-868b-3f977df26e05")
    async def get_groups(self, query: schemas.GroupQuery = Depends()) -> ListT[schemas.Group]:
        count, results = await self.service.list_and_count(self.session, query)
        return ListT(count=count, results=[schemas.Group.model_validate(r) for r in results])

    @router.put("/groups/{id}", operation_id="3d5badd1-665c-49f8-85c4-6f6d7f3a1b2a")
    async def update_group(self, id: int, group: schemas.GroupUpdate) -> IdResponse:
        db_group = await self.service.get_one_or_404(self.session, id, selectinload(Group.user))
        await self.service.update(self.session, db_group, group)
        return IdResponse(id=id)

    @router.delete("/groups/{id}", operation_id="e16830da-2973-4369-8e75-da9b4174ab72")
    async def delete_group(self, id: int) -> IdResponse:
        db_group = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_group)
        return IdResponse(id=id)


@cbv(router)
class RoleAPI:
    user: User = Depends(auth)
    session: AsyncSession = Depends(get_session)
    service = services.role_service

    @router.post("/roles", operation_id="a18a152b-e9e9-4128-b8be-8a8e9c842abb")
    async def create_role(self, role: schemas.RoleCreate) -> IdResponse:
        new_role = await self.service.create(self.session, role)
        return IdResponse(id=new_role.id)

    @router.get("/roles/{id}", operation_id="2b45f59a-77a1-45d4-bf43-94373da517e3")
    async def get_role(self, id: int) -> schemas.Role:
        db_role = await self.service.get_one_or_404(self.session, id, selectinload(Role.permission), undefer_load=True)
        return schemas.Role.model_validate(db_role)

    @router.get("/roles", operation_id="c5f793b1-7adf-4b4e-a498-732b0fa7d758")
    async def get_roles(self, query: schemas.RoleQuery = Depends()) -> ListT[schemas.RoleList]:
        count, results = await self.service.list_and_count(self.session, query)
        return ListT(count=count, results=[schemas.RoleList.model_validate(r) for r in results])

    @router.put("/roles/{id}", operation_id="2fda2e00-ad86-4296-a1d4-c7f02366b52e")
    async def update_role(self, id: int, role: schemas.RoleUpdate) -> IdResponse:
        db_role = await self.service.get_one_or_404(self.session, id, selectinload(Role.permission))
        await self.service.update(self.session, db_role, role)
        return IdResponse(id=id)

    @router.delete("/roles/{id}", operation_id="c4e9e0e8-6b0c-4f6f-9e6c-8d9f9f9f9f9f")
    async def delete_role(self, id: int) -> IdResponse:
        db_role = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_role)
        return IdResponse(id=id)


@cbv(router)
class MenuAPI:
    user: User = Depends(auth)
    session: AsyncSession = Depends(get_session)
    service = services.menu_service

    @router.post("/menus", operation_id="008bf4d4-cc01-48b0-82b8-1a67c0348b31")
    async def create_menu(self, meun: schemas.MenuCreate) -> IdResponse:
        new_menu = await self.service.create(self.session, meun)
        return IdResponse(id=new_menu.id)

    @router.get("/menus", operation_id="cb7f25ab-798b-4668-a838-6339425e2889")
    async def get_menus(self) -> schemas.MenuTree:
        results = await self.service.get_all(self.session)
        data = list_to_tree([r.dict() for r in results])
        return schemas.MenuTree.model_validate(data)

    @router.put("menus/{id}", operation_id="b4d7ac97-a182-4bd1-a75c-6ae44b5fcf0a")
    async def update_menu(self, id: int, meun: schemas.MenuUpdate) -> IdResponse:
        db_menu = await self.service.get_one_or_404(self.session, id)
        await self.service.update(self.session, db_menu, meun)
        return IdResponse(id=id)

    async def delete_menu(self, id: int) -> IdResponse:
        db_menu = await self.service.get_one_or_404(self.session, id)
        await self.service.delete(self.session, db_menu)
        return IdResponse(id=id)


@cbv(router)
class PermissionAPI:
    user: User = Depends(auth)
    session: AsyncSession = Depends(get_session)
    service = services.permission_service

    @router.get("/permissions", operation_id="8057d614-150f-42ee-984c-d0af35796da3", summary="Permissions: Get All")
    async def get_permissions(self) -> list[schemas.Permission]:
        permissions = await services.permission_service.get_all(self.session)
        return [schemas.Permission.model_validate(p) for p in permissions]

    @router.post("/permissions", operation_id="e0fe80d5-cbe0-4c2c-9eff-57e80ecba522", summary="Permissions: Sync All")
    async def sync_db_permission(self, request: Request) -> dict:
        routes = request.app.router.__dict__["routes"]
        operation_ids = []
        router_mappings = {}
        for route in routes:
            if hasattr(route, "tags") and not hasattr(route, "operation_id"):
                msg = f"Missing operation_id for route: {route.path}"
                raise ValueError(msg)
            if not hasattr(route, "operation_id") and not hasattr(route, "tags"):
                continue
            operation_ids.append(route.operation_id)
            router_mappings[route.operation_id] = {
                "name": route.name,
                "url": route.path,
                "method": next(iter(route.methods)),
                "tag": route.tags[0],
            }
        permissions = await self.service.get_multi_by_ids(self.session, operation_ids)
        removed = {str(p.id) for p in permissions} - set(operation_ids)
        added = set(operation_ids) - {str(p.id) for p in permissions}
        if removed:
            await self.service.batch_delete(self.session, [UUID(r) for r in removed])
        if added:
            new_permissions = [Permission(id=p_id, **router_mappings[p_id]) for p_id in added]
            self.session.add_all(new_permissions)
            await self.session.commit()
        return {"added": added, "removed": removed}


@router.get("/health", operation_id="e7372032-61c5-4e3d-b2f1-b788fe1c52ba", summary="Service Health check")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/version", operation_id="47918987-15d9-4eea-8c29-e73cb009a4d5", summary="Get Service Version")
def version() -> dict[str, str]:
    return {"version": settings.VERSION}
