from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncResult, AsyncSession
from sqlalchemy.orm import selectinload

from src.api.auth import schemas
from src.api.auth.models import User
from src.api.base import BaseListResponse, BaseResponse
from src.api.deps import (
    CommonParams,
    audit_without_data,
    common_params,
    get_current_user,
    get_session,
)
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_0, ERR_NUM_10004, ERR_NUM_10005

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class UserCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    audit = Depends(audit_without_data)

    @router.get("/users/{id}")
    async def get_user(self, id: int) -> BaseResponse[schemas.AuthUser]:
        result: AsyncResult = await self.session.execute(
            select(User).where(User.id == id).options(selectinload(User.auth_role))
        )
        local_user: User | None = result.scalars().first()
        if not local_user:
            return ERR_NUM_10004.dict()
        return_info = ERR_NUM_0.dict()
        return_info["data"] = local_user
        return return_info

    @router.get("/users")
    async def get_users(
        self,
        common_params: CommonParams = Depends(common_params),
    ) -> BaseListResponse[List[schemas.AuthUser]]:
        # TODO: confirm query_params
        if not common_params.q:
            result = (
                (
                    await self.session.execute(
                        select(User)
                        .slice(
                            common_params.offset,
                            common_params.limit + common_params.offset,
                        )
                        .options(selectinload(User.auth_role))
                    )
                )
                .scalars()
                .all()
            )
            count = (await self.session.execute(select(func.count(User.id)))).scalar()
            return_info = ERR_NUM_0.dict()
            return_info.update({"data": {"count": count, "results": result}})
            return return_info

    @router.put("/users/{id}")
    async def update_user(
        self,
        id: int,
        user: schemas.AuthUserUpdate,
    ) -> BaseResponse[int]:
        result: AsyncResult = await self.session.execute(
            select(User).where(User.id == id)
        )
        local_user: User | None = result.scalars().first()
        if not local_user:
            return ERR_NUM_10004.dict()
        if user.email is not None:
            existed = (
                (
                    await (
                        self.session.execute(
                            select(User.id).where(User.email == user.email)
                        )
                    )
                )
                .scalars()
                .one_or_none()
            )
            if existed:
                return ERR_NUM_10005.dict()
        await self.session.execute(
            update(User)
            .where(User.id == id)
            .values(
                **user.dict(exclude_none=True).execute_options(
                    synchronize_session="fetch"
                )
            )
        )
        await self.session.commit()
        return_info = ERR_NUM_0.dict()
        return_info["data"] = id
        return return_info

    @router.delete("/users/{id}")
    async def delete_user(self, id: int) -> BaseResponse[int | None]:
        result: AsyncResult = await self.session.execute(
            select(User).where(User.id == id)
        )
        local_user: User | None = result.scalars().first()
        if not local_user:
            return ERR_NUM_10004.dict()
        await self.session.delete(local_user)
        await self.session.commit()
        return_info = ERR_NUM_0.dict()
        return_info.update({"data": id})
        return return_info
