from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, INET
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression

from src.db.db_base import Base
from src.db.db_mixin import AuditLogMixin, NameMixin, TimestampMixin

__all__ = ("Server", "Cluster")


class Server(Base, NameMixin, TimestampMixin, AuditLogMixin):
    __tablename__ = "server"
    id = Column(Integer, primary_key=True)
    status = Column(String, nullable=False)
    role_id = Column(
        Integer, ForeignKey("dcim_device_role.id", ondelete="SET NULL"), nullable=True
    )
    dcim_device_role = relationship(
        "DeviceRole", back_populates="server", overlaps="server"
    )
    platform_id = Column(
        Integer, ForeignKey("dcim_platform.id", ondelete="SET NULL"), nullable=True
    )
    dcim_platform = relationship("Platform", back_populates="server", overlaps="server")
    primary_ipv4 = Column(INET, nullable=True)
    primary_ipv6 = Column(INET, nullable=True)
    tags = Column(ARRAY(String, dimensions=1), nullable=True)
    cluster_id = Column(
        Integer, ForeignKey("cluster.id", ondelete="SET NULL"), nullable=True
    )
    cluster = relationship("Cluster", back_populates="server", overlaps="server")
    is_vm = Column(Boolean, nullable=False, server_default=expression.true())
    cpu = Column(Integer, nullable=True)
    memory = Column(String, nullable=False)
    disk = Column(String, nullable=True)
    contact_id = Column(
        Integer, ForeignKey("contact.id", ondelete="SET NULL"), nullable=True
    )
    contact = relationship("Contact", back_populates="server", overlaps="server")
    owner = Column(String, nullable=True)
    department_id = Column(
        Integer, ForeignKey("department.id", ondelete="SET NULL"), nullable=True
    )
    department = relationship("Department", back_populates="server", overlaps="server")


class Cluster(Base, NameMixin, TimestampMixin, AuditLogMixin):
    __tablename__ = "cluster"
    id = Column(Integer, primary_key=True)
    server = relationship("Server", back_populates="cluster", passive_deletes=True)
    dcim_device = relationship("Device", back_populates="cluster", passive_deletes=True)
