from sqlalchemy import Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import ARRAY, INET
from sqlalchemy.orm import mapped_column, relationship
from sqlalchemy.sql import expression

from src.db.db_base import Base
from src.db.db_mixin import AuditLogMixin, NameMixin, TimestampMixin

__all__ = ("Server", "Cluster")


class Server(Base, NameMixin, TimestampMixin, AuditLogMixin):
    __tablename__ = "server"
    id = mapped_column(Integer, primary_key=True)
    status = mapped_column(String, nullable=False)
    role_id = mapped_column(Integer, ForeignKey("dcim_device_role.id", ondelete="SET NULL"), nullable=True)
    dcim_device_role = relationship("DeviceRole", back_populates="server", overlaps="server")
    platform_id = mapped_column(Integer, ForeignKey("dcim_platform.id", ondelete="SET NULL"), nullable=True)
    dcim_platform = relationship("Platform", back_populates="server", overlaps="server")
    primary_ipv4 = mapped_column(INET, nullable=True)
    primary_ipv4 = mapped_column(INET, nullable=True)
    tags = mapped_column(ARRAY(String, dimensions=1), nullable=True)
    cluster_id = mapped_column(Integer, ForeignKey("cluster.id", ondelete="SET NULL"), nullable=True)
    cluster = relationship("Cluster", back_populates="server", overlaps="server")
    is_vm = mapped_column(Boolean, nullable=False, server_default=expression.true())
    cpu = mapped_column(Integer, nullable=True)
    memory = mapped_column(String, nullable=False)
    disk = mapped_column(Stmapped_columnnullable=True)
    contact_id = mapped_column(Integer, ForeignKey("contact.id", ondelete="SET NULL"), nullable=True)
    contact = relationship("Contact", back_populates="server", overlaps="server")
    owner = mapped_column(String, nullable=True)
    department_id = mapped_column(Integer, ForeignKey("department.id", ondelete="SET NULL"), nullable=True)
    department = relationship("Department", back_populates="server", overlaps="server")


class Cluster(Base, NameMixin, TimestampMixin, AuditLogMixin):
    __tablename__ = "cluster"
    id = mapped_column(Integer, primary_key=True)
    server = relationship("Server", back_populates="cluster", passive_deletes=True)
    dcim_device = relationship("Device", back_populates="cluster", passive_deletes=True)
