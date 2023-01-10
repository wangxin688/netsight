from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm import selectinload

from src.app.auth import schemas
from src.app.auth.models import Group, Permission, Role, User
from src.app.base import BaseListResponse, BaseResponse, QueryParams
from src.app.deps import audit_without_data, get_current_user, get_session
from src.db.crud_base import CRUDBase
from src.register.middleware import AuditRoute
from src.utils.error_code import (
    ERR_NUM_10004,
    ERR_NUM_10005,
    ERR_NUM_10006,
    ERR_NUM_10007,
    ERR_NUM_10008,
    ERR_NUM_10009,
    ResponseMsg,
)

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class AuthUserCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    audit = Depends(audit_without_data)
    crud = CRUDBase(User)

    @router.get("/users/{id}")
    async def get_user(self, id: int) -> BaseResponse[schemas.AuthUser]:
        """get the user"""
        local_user: AsyncResult = await self.session.get(
            User, id, options=(selectinload(User.auth_role),)
        )
        if not local_user:
            return ERR_NUM_10004.dict()
        return_info = ResponseMsg(data=local_user)
        return return_info

    @router.get("/users")
    async def get_users(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.AuthUserBase]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (await self.session.execute(select(func.count(User.id)))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/users/getList")
    async def get_users_filter(
        self,
        user: schemas.AuthUserQuery,
    ) -> BaseListResponse[List[schemas.AuthUser]]:
        pass

    @router.put("/users/{id}")
    async def update_user(
        self,
        id: int,
        user: schemas.AuthUserUpdate,
    ) -> BaseResponse[int]:
        local_user = await self.session.get(
            User, id, options=(selectinload(User.auth_group),)
        )
        if not local_user:
            return ERR_NUM_10004.dict()
        if user.email is not None:
            existed = await self.crud.get_by_field(self.session, "email", user.email)
            if existed:
                return ERR_NUM_10005.dict()
        if user.auth_group_ids:
            groups: List[Group] = local_user.auth_group
            group_ids = [group.id for group in groups]
            for group in groups:
                if group.id not in user.auth_group_ids:
                    local_user.auth_group.remove(group)
            for user_group_id in user.auth_group_ids:
                if user_group_id not in group_ids:
                    auth_group: Group = await self.session.get(Group, user_group_id)
                    if auth_group:
                        local_user.auth_group.append(auth_group)
        if not user.password:
            await self.session.execute(
                update(User)
                .where(User.id == id)
                .values(
                    **user.dict(
                        exclude_none=True, exclude={"auth_group_ids"}
                    ).execute_options(synchronize_session="fetch")
                )
            )
        else:
            await self.session.execute(
                update(User)
                .where(User.id == id)
                .values(
                    **user.dict(
                        exclude_none=True, exclude={"auth_group_ids", "password2"}
                    ).execute_options(synchronize_session="fetch")
                )
            )
        await self.session.commit()
        return_info = ResponseMsg(data=local_user.id)
        return return_info

    @router.delete("/users/{id}")
    async def delete_user(self, id: int) -> BaseResponse[int]:
        local_user = await self.crud.delete(self.session, id)
        if not local_user:
            return ERR_NUM_10004.dict()
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/users/deleteList")
    async def delete_users(
        self, user: schemas.AuthUserBulkDelete
    ) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, user.ids)
        if not results:
            return ERR_NUM_10004.dict()
        return_info = ResponseMsg(data=[d.id for d in results])
        return return_info


@cbv(router)
class AuthGroupCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    audit = Depends(audit_without_data)
    crud = CRUDBase(Group)

    @router.post("/groups")
    async def create_group(
        self, group: schemas.AuthGroupCreate
    ) -> BaseResponse[int | None]:
        local_group = await self.crud.get_by_field(self.session, "name", group.name)
        if local_group is not None:
            return ERR_NUM_10006.dict()
        new_group = Group(**group.dict(exclude={"auth_user_ids"}))
        self.session.add(new_group)
        await self.session.flush()
        if not group.auth_user_ids:
            await self.session.commit()
            return_info = ResponseMsg(data=id)
            return return_info
        user_curd = CRUDBase(User)
        users = await user_curd.get_multi(self.session, group.auth_user_ids)
        for user in users:
            new_group.auth_user.append(user)
        self.session.add(new_group)
        await self.session.commit()
        return_info = ResponseMsg(data=id)
        return return_info

    @router.get("/groups/{id}")
    async def get_group(self, id: int) -> BaseResponse[schemas.AuthGroup]:
        local_group = await self.session.get(
            Group, id, options=(selectinload(Group.auth_user),)
        )
        if not local_group:
            return ERR_NUM_10007
        return_info = ResponseMsg(data=local_group)
        return return_info

    @router.get("/groups")
    async def get_groups_all(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.AuthGroupBase]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (await self.session.execute(func.count(Group.id))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/groups/getList")
    async def get_groups(
        self, group: schemas.AuthGroupQuery
    ) -> BaseListResponse[List[schemas.AuthGroup]]:
        pass

    @router.put("/groups/{id}")
    async def update_group(
        self,
        id: int,
        group: schemas.AuthGroupUpdate,
    ) -> BaseResponse[int]:
        local_group = await self.session.get(
            Group, id, options=(selectinload(Group.auth_user),)
        )
        if not local_group:
            return ERR_NUM_10007
        if group.auth_user_ids:
            users: List[User] = local_group.auth_user
            user_ids = [user.id for user in users]
            for user in users:
                if user.id not in group.user_ids:
                    local_group.auth_user.remove(user)
            for auth_user_id in group.auth_user_ids:
                if auth_user_id not in user_ids:
                    _auth_user: User = await self.session.get(User, auth_user_id)
                    if _auth_user:
                        local_group.auth_user.append(_auth_user)
        self.session.execute(
            update(Group)
            .where(Group.id == id)
            .values(**group.dict(exclude={"auth_user_ids"}, exclude_none=True))
            .execute_options(synchronize_session="fetch")
        )
        await self.session.commit()
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/groups/{id}")
    async def delete_group(self, id: int) -> BaseResponse[int]:
        local_group = await self.crud.delete(self.session, id)
        if not local_group:
            return ERR_NUM_10007
        return_info = ResponseMsg(data=id)
        return return_info


@cbv(router)
class AuthRoleCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    audit = Depends(audit_without_data)
    crud = CRUDBase(Role)

    @router.post("/roles")
    async def create_role(
        self,
        role: schemas.AuthRoleCreate,
    ) -> BaseResponse[int]:
        local_role = await self.crud.get_by_field(self.session, "name", role.name)
        if local_role is not None:
            return ERR_NUM_10008.dict()
        new_role = Role(**role.dict(exclude={"auth_user_ids", "auth_permission_ids"}))
        self.session.add(new_role)
        await self.session.flush()
        perm_crud = CRUDBase(Permission)
        if role.auth_permission_ids:
            permissions: List[Permission] = perm_crud.get_multi(
                self.session, role.auth_permission_ids
            )
            if permissions:
                for permission in permissions:
                    new_role.auth_permission.append(permission)
        await self.session.commit()
        return_info = ResponseMsg(data=new_role.id)
        return return_info

    @router.get("/roles/{id}")
    async def get_role(self, id: int) -> BaseResponse[schemas.AuthRole]:
        role: Role = await self.session.get(
            Role, id, options=(selectinload(Role.auth_permission),)
        )
        if not role:
            return ERR_NUM_10009.dict()
        return_info = ResponseMsg(data=role)
        return return_info

    @router.get("/roles")
    async def get_roles(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.AuthRoleBase]]:
        local_roles = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (await self.session.execute(select(func.count(Role.id)))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": local_roles})
        return return_info

    @router.post("/roles/getList")
    async def get_roles_filter(
        self,
        role: schemas.AuthRoleQuery,
    ) -> BaseListResponse[List[schemas.AuthRole]]:
        pass

    @router.put("/roles/{id}")
    async def update_role(
        self,
        id: int,
        role: schemas.AuthRoleUpdate,
    ) -> BaseResponse[int]:
        local_role = await self.crud.get(
            Role, id, options=(selectinload(Role.auth_permission),)
        )
        if not local_role:
            return ERR_NUM_10009
        if role.auth_permission_ids:
            permissions: List[Permission] = local_role.auth_permission
            permission_ids = [permission.id for permission in permissions]
            for permission in permissions:
                if permission.id not in role.auth_permission_ids:
                    local_role.auth_permission.remove(permission)
            for auth_permission_id in role.auth_permission_ids:
                if auth_permission_id not in permission_ids:
                    _auth_permission: Permission = self.session.get(
                        Permission, auth_permission_id
                    )
                    if _auth_permission:
                        local_role.auth_user.append(_auth_permission)
        self.session.execute(
            update(Role)
            .where(Role.id == id)
            .values(**role.dict(exclude={"auth_permission_ids"}, exclude_none=True))
            .execute_options(synchronize_session="fetch")
        )
        await self.session.commit()
        return_info = ResponseMsg(data=id)
        return return_info

    @router.delete("/roles/{id}")
    async def delete_role(self, id: int) -> BaseResponse[int]:
        local_role = await self.crud.delete(self.session, id)
        if not local_role:
            return ERR_NUM_10007
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/roles/deleteList")
    async def delete_roles(
        self, role: schemas.AuthRoleBulkDelete
    ) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, role.ids)
        if not results:
            return ERR_NUM_10007
        return_info = ResponseMsg(data=[d.id for d in results])
        return return_info
