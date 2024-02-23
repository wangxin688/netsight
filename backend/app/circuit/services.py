from typing import TYPE_CHECKING

from sqlalchemy.orm import selectinload

from app.circuit import schemas
from app.db import Circuit, Device, Interface, Site
from app.db.dtobase import DtoBase

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class CircuitDto(DtoBase[Circuit, schemas.CircuitCreate, schemas.CircuitUpdate, schemas.CircuitQuery]):
    async def get_interface_info(self, session: "AsyncSession", interface_id: int) -> tuple[int, int]:
        interface_dto = DtoBase(Interface)
        interface = await interface_dto.get_one_or_404(
            session,
            interface_id,
            selectinload(Interface.device).load_only(Device.id).selectinload(Device.site).load_only(Site.id),
        )

        return interface.device.id, interface.device.site.id
