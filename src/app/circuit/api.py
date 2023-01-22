from typing import List

from fastapi import Depends
from fastapi_utils.cbv import cbv
from fastapi_utils.inferring_router import InferringRouter
from loguru import logger
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.auth.models import User
from src.app.base import BaseListResponse, BaseResponse, QueryParams
from src.app.circuit import schemas
from src.app.circuit.models import Circuit, CircuitType, Provider
from src.app.deps import get_current_user, get_locale, get_session
from src.app.netsight.models import Contact
from src.db.crud_base import CRUDBase
from src.register.middleware import AuditRoute
from src.utils.error_code import ERR_NUM_404, ERR_NUM_409, ResponseMsg, error_404_409

router = InferringRouter(route_class=AuditRoute)


@cbv(router)
class ProviderCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Provider)
    locale = Depends(get_locale)

    @router.post("/providers")
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
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "provider", "name", provider.name
            )
            return return_info
        return_info = ResponseMsg(data=new_provider.id, locale=self.locale)
        return return_info

    @router.get("/providers/{id}")
    async def get_provider(self, id: int) -> BaseResponse[schemas.Provider]:
        result = await self.session.get(Provider, id)
        if result is None:
            return_info = error_404_409(ERR_NUM_404, self.locale, "provider", "#id", id)
            return return_info
        return_info = ResponseMsg(data=result, locale=self.locale)
        return return_info

    @router.get("/providers")
    async def get_providers(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.ProviderBase]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(
            data={"count": count, "results": results}, locale=self.locale
        )
        return return_info

    @router.post("/providers/getList")
    async def get_providers_filter(
        self, provider: schemas.ProviderQuery
    ) -> BaseListResponse[List[schemas.Provider]]:
        pass

    @router.put("/providers/{id}")
    async def update_provider(self, id: int, provider: schemas.ProviderUpdate):
        result: Provider | None = await self.session.get(Provider, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "provider", "#id", id)
            return return_info
        if provider.name:
            exist: Provider = await self.crud.get_by_field(
                self.session, "name", provider.name
            )
            if exist:
                return_info = error_404_409(
                    ERR_NUM_409, self.locale, "provider", "name", provider.name
                )
                return return_info
        await self.crud.update(self.session, id, provider)
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/provider/updateList")
    async def update_providers(
        self, provider: schemas.ProviderBulkUpdate
    ) -> BaseResponse[List[int]]:
        results = await self.crud.get_multi(self.session, provider.ids)
        diff_provider: set = set(provider.ids) - set(
            [provider.id for provider in results]
        )
        if diff_provider:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "provider", "#ids", list(diff_provider)
            )
            return return_info
        await self.crud.update_multi(self.session, provider.ids, excludes={"ids"})
        return_info = ResponseMsg(data=provider.ids, locale=self.locale)
        return return_info

    @router.delete("/providers/{id}")
    async def delete_provider(self, id: int) -> BaseResponse[int]:
        local_provider: Provider | None = await self.crud.delete(self.session, id)
        if not local_provider:
            return_info = error_404_409(ERR_NUM_404, self.locale, "provider", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/providers/deleteList")
    async def delete_providers(
        self, provider: schemas.ProviderBulkDelete
    ) -> BaseListResponse[List[schemas.ProviderBase]]:
        local_providers = await self.crud.delete_multi(self.session, provider.ids)
        if not local_providers:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "provider", "#ids", provider.ids
            )
            return return_info
        return_info = ResponseMsg(data=provider.ids, locale=self.locale)
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
        result = await self.crud.get_by_field(self.session, "name", circuit_type.name)
        if result is not None:
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "circuit_type", "name", circuit_type.name
            )
            return return_info
        new_circuit_type = CircuitType(**circuit_type.dict())
        await self.session.add(new_circuit_type)
        await self.session.commit()
        return_info = ResponseMsg(data=new_circuit_type.id, locale=self.locale)
        return return_info

    @router.get("/circuit-types/{id}")
    async def get_circuit_type(self, id: int) -> BaseResponse[schemas.CircuitType]:
        result = await self.session.get(CircuitType, id)
        if not result:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "circuit_type", "#id", id
            )
            return return_info
        return_info = ResponseMsg(data=result, locale=self.locale)
        return return_info

    @router.get("/circuit-types")
    async def get_circuit_types(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.CircuitType]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(
            data={"count": count, "results": results}, locale=self.locale
        )
        return return_info

    @router.post("/circuit-types/getList")
    async def get_circuit_types_filter(
        self, circuit_type: schemas.CircuitTypeQuery
    ) -> BaseListResponse[List[schemas.CircuitType]]:
        pass

    @router.put("/circuit-types/{id}")
    async def update_circuit_type(
        self, circuit_type: schemas.CircuitTypeUpdate
    ) -> BaseResponse[int]:
        local_circuit_type: CircuitType | None = await self.session.get(CircuitType, id)
        if not local_circuit_type:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "circuit_type", "#id", id
            )
            return return_info

        try:
            await self.crud.update(self.session, id, circuit_type)
        except IntegrityError as e:
            logger.error(e)
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "circuit_type", "name", circuit_type.name
            )
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/circuits/updateList")
    async def update_circuit_types(self):
        """not implemented yet"""

    @router.delete("/circuits/{id}")
    async def delete_circuit_type(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "circuit_type", "#id", id
            )
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/circuits/deleteList")
    async def delete_circuit_types(
        self, circuit_type: schemas.CircuitTypeBulkDelete
    ) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, circuit_type.ids)
        if not results:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "circuit_type", "#ids", circuit_type.ids
            )
            return return_info
        return_info = ResponseMsg(
            data=[result.id for result in results], locale=self.locale
        )
        return return_info


@cbv(router)
class CircuitCBV:
    session: AsyncSession = Depends(get_session)
    current_user: User = Depends(get_current_user)
    crud = CRUDBase(Circuit)
    locale = Depends(get_locale)

    @router.post("/circuits")
    async def create_circuit(self, circuit: schemas.CircuitCreate) -> BaseResponse[int]:
        if circuit.provider_id:
            provider: Provider = await self.session.get(Provider, circuit.provider_id)
            if not provider:
                return_info = error_404_409(
                    ERR_NUM_404, self.locale, "provider", "#id", id
                )
                return return_info
        new_circuit = Circuit(circuit.dict(exclude={"contact_id"}))
        try:
            self.session.add(new_circuit)
            await self.session.commit()
        except IntegrityError as e:
            logger.error(e)
            return_info = error_404_409(
                ERR_NUM_409, self.locale, "circuit", "name", circuit.name
            )
            return return_info
        if circuit.contact_id:
            contacts: List[Contact] = await self.crud.get_multi(
                self.session, circuit.contact_id
            )
            if len(contacts) < circuit.contact_id or not contacts:
                if not contacts:
                    diff_contacts = circuit.contact_id
                else:
                    diff_contacts = set(circuit.contact_id) - set(
                        [contact.id for contact in contacts]
                    )
                return_info = error_404_409(
                    ERR_NUM_404, self.locale, "contact", "#id", diff_contacts
                )
                return return_info
            new_circuit.contact.append(contacts)
            await self.session.commit()
        return_info = ResponseMsg(data=new_circuit.id)
        return return_info

    @router.get("/circuits/{id}")
    async def get_circuit(self, id: int) -> BaseResponse[schemas.Circuit]:
        local_circuit: Circuit = await self.session.get(Circuit, id)
        if not local_circuit:
            return_info = error_404_409(ERR_NUM_404, self.locale, "circuit", "#id", id)
            return return_info
        return_info = ResponseMsg(data=local_circuit, locale=self.locale)
        return return_info

    @router.get("/circuits")
    async def get_circuits(
        self, q: QueryParams = Depends(QueryParams)
    ) -> BaseListResponse[List[schemas.Circuit]]:
        results = await self.crud.get_all(self.session, q.limit, q.offset)
        count = await self.crud.count_all(self.session)
        return_info = ResponseMsg(
            data={"count": count, "results": results}, locale=self.locale
        )
        return return_info

    @router.post("/circuits/getList")
    async def get_circuits_filter(
        self, circuit: schemas.CircuitQuery
    ) -> BaseListResponse[List[schemas.Circuit]]:
        pass

    @router.put("/circuits/{id}")
    async def update_circuit(
        self, id: int, circuit: schemas.CircuitUpdate
    ) -> BaseResponse[int]:
        result: Circuit = await self.session.get(Circuit, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "circuit", "#id", id)
            return return_info

    @router.post("/circuits/updateList")
    async def update_circuits(
        self, circuit: schemas.CircuitBulkUpdate
    ) -> BaseResponse[List[int]]:
        pass

    @router.delete("/circuits/{id]")
    async def delete_circuit(self, id: int) -> BaseResponse[int]:
        result = await self.crud.delete(self.session, id)
        if not result:
            return_info = error_404_409(ERR_NUM_404, self.locale, "circuit", "#id", id)
            return return_info
        return_info = ResponseMsg(data=id, locale=self.locale)
        return return_info

    @router.post("/circuits/deleteList")
    async def delete_circuits(
        self, circuit: schemas.CircuitBulkDelete
    ) -> BaseResponse[List[int]]:
        results = await self.crud.delete_multi(self.session, circuit.ids)
        if not results:
            return_info = error_404_409(
                ERR_NUM_404, self.locale, "circuit", "#ids", circuit.ids
            )
            return return_info
        return_info = ResponseMsg(data=[result.id for result in results])
        return return_info
