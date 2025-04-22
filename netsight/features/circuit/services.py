from typing import TYPE_CHECKING

from sqlalchemy.orm import selectinload

from netsight.core.repositories import BaseRepository
from netsight.features.circuit import schemas
from netsight.features.circuit.models import ISP, Circuit
from netsight.features.dcim.models import Device, Interface
from netsight.features.org.models import Site

__all__ = ("circuit_service", "isp_service")

if TYPE_CHECKING:
    from sqlalchemy.ext.asyncio import AsyncSession


class CircuitService(BaseRepository[Circuit, schemas.CircuitCreate, schemas.CircuitUpdate, schemas.CircuitQuery]):
    async def get_interface_info(self, session: "AsyncSession", interface_id: int) -> tuple[int, int]:
        interface_service = BaseRepository(Interface)
        interface = await interface_service.get_one_or_404(
            session,
            interface_id,
            selectinload(Interface.device).load_only(Device.id).selectinload(Device.site).load_only(Site.id),
        )

        return interface.device.id, interface.device.site.id


class ISPService(BaseRepository[ISP, schemas.ISPCreate, schemas.ISPUpdate, schemas.ISPQuery]):
    pass


circuit_service = CircuitService(Circuit)
isp_service = ISPService(ISP)
