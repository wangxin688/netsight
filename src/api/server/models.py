from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from src.db.db_base import Base
from src.db.db_mixin import NameMixin, PrimaryKeyMixin, TimestampMixin


class Server(Base, PrimaryKeyMixin, NameMixin, TimestampMixin):
    __tablename__ = "server"
    status = Column(String, nullable=False)
    role_id = Column(
        Integer, ForeignKey("dcim_device_role.id", ondelete="SET NULL"), nullable=True
    )
    role = relationship("DeviceRole", back_populate="server", overlaps="server")
    platform_id = Column(
        Integer, ForeignKey("dcim_platform.id", ondelete="SET NULL"), nullable=True
    )
    platform = relationship("DevicePlatform", back_populate="server", overlaps="server")
    tenant_id = Column(
        Integer, ForeignKey("tenant.id", ondelete="CASCADE"), nullable=True
    )
    tenant = relationship("Tenant", back_populate="server", overlaps="server")
    primary_ipv4 = Column(INET, nullable=True)
    primary_ipv6 = Column(INET, nullable=True)
    tags = Column(ARRAY(String, dimensions=1), nullable=True)
    cluster_id = Column(
        Integer, ForeignKey("cluster.id", ondelete="SET NULL"), nullable=True
    )
    is_vm = Column(Boolean, nullable=False, server_default=expression.true())
    cpu = Column(Integer, nullable=True)
    memory = Column(String, nullable=False)
    disk = Column(String, nullable=True)
    contact_id = Column(
        Integer, ForeignKey("contact.id", ondelete="SET NULL"), nullable=True
    )
    contact = relationship("Contant", back_populate="server", overlaps="server")


class Cluster(Base, PrimaryKeyMixin, NameMixin, TimestampMixin):
    __tablename__ = "cluster"
    server = relationship("Server", back_populate="cluster", overlaps="cluster")
