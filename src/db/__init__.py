from sqlalchemy import and_, func, select
from sqlalchemy.orm import column_property

from src.db.base import Base
from src.arch.models import *
from src.auth.models import *
from src.circuit.models import *
from src.dcim.models import *
from src.ipam.models import *
from src.netconfig.models import *
from src.org.models import *


def orm_by_table_name(table_name: str) -> type[Base] | None:
    for m in Base.registry.mappers:
        if getattr(m.class_, "__tablename__", None) == table_name:
            return m.class_
    return None


IPRole.prefix_count = column_property(
    select(func.count(Prefix.id)).where(Prefix.role_id == IPRole.id).scalar_subquery(),
)

Platform.textfsm_template_count = column_property(
    select(func.count(TextFsmTemplate.id))
    .where(TextFsmTemplate.platform_id == Platform.id)
    .correlate_except(Platform)
    .scalar_subquery(),
    deferred=True,
)

ASN.site_count = column_property(
    select(func.count(Site.id)).where(and_(SiteASN.asn_id == ASN.id, SiteASN.site_id == Site.id)).scalar_subquery(),
    deferred=True,
)
ASN.isp_count = column_property(
    select(func.count(ISP.id)).where(and_(ISPASN.asn_id == ASN.id, ISPASN.isp_id == ISP.id)).scalar_subquery(),
    deferred=True,
)

IPRole.vlan_count = column_property(
    select(func.count(VLAN.id)).where(VLAN.role_id == IPRole.id).correlate_except(IPRole).scalar_subquery(),
    deferred=True,
)
CircuitType.circuit_count = column_property(
    select(func.count(Circuit.id))
    .where(Circuit.circuit_type_id == CircuitType.id)
    .correlate_except(CircuitType)
    .scalar_subquery(),
    deferred=True,
)
DeviceRole.device_count = column_property(
    select(func.count(Device.id))
    .where(Device.device_role_id == DeviceRole.id)
    .correlate_except(DeviceRole)
    .scalar_subquery(),
    deferred=True,
)
RackRole.rack_count = column_property(
    select(func.count(Rack.id)).where(Rack.rack_role_id == RackRole.id).correlate_except(RackRole).scalar_subquery(),
    deferred=True,
)
