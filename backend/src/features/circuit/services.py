from typing import TYPE_CHECKING

from sqlalchemy.orm import selectinload

from src.core.repositories import BaseRepository
from src.features.circuit import schemas
from src.features.circuit.models import Circuit
from src.features.dcim.models import Device, Interface
from src.features.org.models import Site

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class CircuitDto(BaseRepository[Circuit, schemas.CircuitCreate, schemas.CircuitUpdate, schemas.CircuitQuery]):
    async def get_interface_info(self, session: "AsyncSession", interface_id: int) -> tuple[int, int]:
        interface_dto = BaseRepository(Interface)
        interface = await interface_dto.get_one_or_404(
            session,
            interface_id,
            selectinload(Interface.device).load_only(Device.id).selectinload(Device.site).load_only(Site.id),
        )

        return interface.device.id, interface.device.site.id
