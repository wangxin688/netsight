from sqlalchemy import Column, Integer, String

from src.db.db_base import Base
from src.db.db_mixin import NameMixin


class AccessPointGroup(Base):
    __tablename__ = "wlan_access_point_group"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)


class AccessPoint(Base, NameMixin):
    __tablename__ = "wlan_access_point"
    id = Column(Integer, primary_key=True)
    status = Column()


class SSID(Base, NameMixin):
    __tablename__ = "wlan_ssid"
    id = Column(Integer, primary_key=True)
