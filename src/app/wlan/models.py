from sqlalchemy import Integer, String
from sqlalchemy.orm import mapped_column

from src.db.db_base import Base
from src.db.db_mixin import NameMixin


class AccessPointGroup(Base):
    __tablename__ = "wlan_access_point_group"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String, nullable=False, unique=True)
    description = mapped_column(String, nullable=True)


class AccessPoint(Base, NameMixin):
    __tablename__ = "wlan_access_point"
    id = mapped_column(Integer, primary_key=True)
    status = mapped_column()


class SSID(Base, NameMixin):
    __tablename__ = "wlan_ssid"
    id = mapped_column(Integer, primary_key=True)
