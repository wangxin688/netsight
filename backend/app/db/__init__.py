from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import column_property

from app.arch.models import *
from app.auth.models import *
from app.circuit.models import *
from app.db.database import Base
from app.dcim.models import *
from app.ipam.models import *
from app.netconfig.models import *
from app.org.models import *


def orm_by_table_name(table_name: str) -> type[Base] | None:
    for m in Base.registry.mappers:
        if getattr(m.class_, "__tablename__", None) == table_name:
            return m.class_
    return None


IPRole.prefix_count = column_property(
    select(func.count(Prefix.id)).where(Prefix.role_id == IPRole.id).scalar_subquery(),
)

Platform.textfsm_template_count = column_property(
    select(func.count(TextFsmTemplate.id)).where(TextFsmTemplate.platform_id == Platform.id).scalar_subquery(),
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
    select(func.count(VLAN.id)).where(VLAN.role_id == IPRole.id).scalar_subquery(),
    deferred=True,
)
CircuitType.circuit_count = column_property(
    select(func.count(Circuit.id)).where(Circuit.circuit_type_id == CircuitType.id).scalar_subquery(),
    deferred=True,
)
DeviceRole.device_count = column_property(
    select(func.count(Device.id)).where(Device.device_role_id == DeviceRole.id).scalar_subquery(),
    deferred=True,
)
RackRole.rack_count = column_property(
    select(func.count(Rack.id)).where(Rack.rack_role_id == RackRole.id).scalar_subquery(),
    deferred=True,
)

Site.device_count = column_property(
    select(func.count(Device.id)).where(Device.site_id == Site.id).scalar_subquery(),
    deferred=True,
)
Site.circuit_count = column_property(
    select(func.count(Circuit.id))
    .where(or_(Circuit.site_a_id == Site.id, Circuit.site_z_id == Site.id))
    .scalar_subquery(),
    deferred=True,
)
Site.prefix_count = column_property(
    select(func.count(Prefix.id)).where(Prefix.site_id == Site.id).scalar_subquery(),
    deferred=True,
)
Site.vlan_count = column_property(
    select(func.count(VLAN.id)).where(VLAN.site_id == Site.id).scalar_subquery(),
    deferred=True,
)
Site.rack_count = column_property(
    select(func.count(Rack.id)).where(Rack.site_id == Site.id).scalar_subquery(),
    deferred=True,
)
Site.asn_count = column_property(
    select(func.count(ASN.id)).where(and_(SiteASN.site_id == Site.id, SiteASN.asn_id == ASN.id)).scalar_subquery(),
    deferred=True,
)
Site.ap_count = column_property(
    select(func.count(AP.id)).where(AP.site_id == AP.id).scalar_subquery(),
    deferred=True,
)
