from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from loguru import logger
from sqlalchemy import func, select, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth.models import User
from src.api.base import BaseListResponse, BaseResponse, QueryParams
from src.api.circuit import schemas
from src.api.circuit.models import CircuitType, Provider
from src.api.deps import get_current_user, get_session
from src.db.crud_base import CRUDBase
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_4004, ERR_NUM_4009, ResponseMsg

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class ProviderCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Provider)

    @router.post("providers")
    async def create_provider(
        self, provider: schemas.ProviderCreate
    ) -> BaseResponse[int]:
        new_provider = Provider(**provider.dict())
        self.session.add(new_provider)
        try:
            await self.session.commit()
        except IntegrityError as e:
            logger.enable(e)
            await self.session.rollback()
            return_info = ERR_NUM_4009
            return_info.msg = f"Create provider failed, provider with name: `{provider.name}` already exists"
            return return_info
        return_info = ResponseMsg(data=new_provider.id)
        return return_info

    @router.get("/providers/{id}")
    async def get_provider(self, id: int) -> BaseResponse[schemas.Provider]:
        local_provider = await self.session.get(Provider, id)
        if local_provider is None:
            return_info = ERR_NUM_4004
            return_info.msg = f"Provider #{id} not found"
            return return_info
        return_info = ResponseMsg(data=local_provider)
        return return_info

    @router.get("/providers")
    async def get_providers(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.ProviderBase]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = (await self.session.execute(select(func.count(Provider.id)))).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/providers/getList")
    async def get_providers_filter(
        self, provider: schemas.ProviderQuery
    ) -> BaseListResponse[List[schemas.Provider]]:
        pass

    @router.put("/providers/{id}")
    async def update_provider(self, id: int, provider: schemas.ProviderUpdate):
        local_provider: Provider | None = await self.session.get(Provider, id)
        if not local_provider:
            return_info = ERR_NUM_4004
            return_info.msg = "Update provider failed, provider #{id} not found"
            return return_info
        stmt = (
            update(Provider)
            .where(Provider.id == id)
            .values(
                **provider.dict(exclude_none=True).execute_options(
                    synchronize_session="fetch"
                )
            )
        )
        await self.session.execute(stmt)
        await self.session.commit()
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/provider/updateList")
    async def update_providers(
        self, provider: schemas.ProviderBulkUpdate
    ) -> BaseResponse[List[int]]:
        local_providers = await self.crud.get_multi(self.session, provider.ids)
        diff_provider: set = set(provider.ids) - set(
            [provider.id for provider in local_providers]
        )
        if diff_provider:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Bulk update provider failed, region #{list(diff_provider)} not found"
            )
            return return_info
        await self.session.execute(
            update(Provider)
            .where(Provider.id.in_(provider.ids))
            .values(provider.dict(exclude={"ids"}, exclude_none=True))
            .execute_options(synchronize_session="fetch")
        )
        await self.session.commit()
        return_info = ResponseMsg(data=provider.ids)
        return return_info

    @router.delete("/providers/{id}")
    async def delete_provider(self, id: int) -> BaseResponse[int]:
        local_provider: Provider | None = await self.crud.delete(self.session, id)
        if not local_provider:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete Provider failed, provider #{id} not found"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/providers/deleteList")
    async def delete_providers(
        self, provider: schemas.ProviderBulkDelete
    ) -> BaseListResponse[List[schemas.ProviderBase]]:
        local_providers = await self.crud.delete_multi(self.session, provider.ids)
        if not local_providers:
            return_info = ERR_NUM_4004
            return_info.msg = f"Delete region failed, region #{provider.ids} not found"
            return return_info
        return_info = ResponseMsg(data=provider.ids)
        return return_info


@cbv(router)
class CircuitTypeCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(CircuitType)

    @router.post("/circuit-types")
    async def create_circuit_type(
        self, circuit_type: schemas.CircuitTypeCreate
    ) -> BaseResponse[int]:
        local_circuit_type = await self.crud.get_by_field(
            self.session, "name", circuit_type.name
        )
        if local_circuit_type is not None:
            return_info = ERR_NUM_4009
            return_info.msg = "Create circuit type failed, circuit type with name {circuit_type.name} already exists."
            return return_info
        new_circuit_type = CircuitType(**circuit_type.dict())
        await self.session.add(new_circuit_type)
        await self.session.commit()
        return_info = ResponseMsg(data=new_circuit_type.id)
        return return_info

    @router.get("/circuit-types/{id}")
    async def get_circuit_type(self, id: int) -> BaseResponse[schemas.CircuitType]:
        local_circuit_type = await self.session.get(CircuitType, id)
        if not local_circuit_type:
            return_info = ERR_NUM_4004
            return_info.msg = f"Circuit type #{id} not found"
        return_info = ResponseMsg(data=local_circuit_type)
        return return_info

    @router.get("/circuit-types")
    async def get_circuit_types(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.CircuitType]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count: int = (
            await self.session.execute(select(func.count(CircuitType.id)))
        ).scalar()
        return_info = ResponseMsg(data={"count": count, "results": results})
        return return_info

    @router.post("/circuit-types/getList")
    async def get_circuit_types_filter(
        self, circuit_type: schemas.CircuitTypeQuery
    ) -> BaseListResponse[List[CircuitType]]:
        pass

    @router.update("/circuit-types/{id}")
    async def update_circuit_type(
        self, circuit_type: schemas.CircuitTypeUpdate
    ) -> BaseResponse[int]:
        local_circuit_type: CircuitType | None = await self.session.get(CircuitType, id)
        if not local_circuit_type:
            return_info = ERR_NUM_4004
            return_info.msg = "Update circuit type failed, circuit type #{id} not found"
            return return_info

        try:
            await self.crud.update(self.session, id, circuit_type)
        except IntegrityError as e:
            logger.error(e)
            return_info = ERR_NUM_4009
            return_info.msg = f"Update circuit type failed, circuit type with name #{circuit_type.name} already exists"
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/circuits/updateList")
    async def update_circuit_types(self):
        """not implemented yet"""

    @router.delete("/circuits/{id}")
    async def delete_circuit_type(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = ERR_NUM_4004
            return_info.msg = (
                f"Deleting circuit type failed, circuit type #{id} not found"
            )
            return return_info
        return_info = ResponseMsg(data=id)
        return return_info

    @router.post("/circuits/deleteList")
    async def delete_circuit_types(
        self, circuit_type: schemas.CircuitTypeBulkDelete
    ) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, circuit_type.ids)
        if not results:
            return_info = ERR_NUM_4004
            return_info.msg = f"Deleted circuit types failed, circuit types #{circuit_type.ids} not found"
            return return_info
        return_info = ResponseMsg(data=circuit_type.ids)
        return return_info
