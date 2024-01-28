from src.arch.models import *
from src.auth.models import *
from src.circuit.models import *
from src.db.base import Base
from src.dcim.models import *
from src.ipam.models import *
from src.netconfig.models import *
from src.org.models import *


def orm_by_table_name(table_name: str) -> type[Base] | None:
    for m in Base.registry.mappers:
        if getattr(m.class_, "__tablename__", None) == table_name:
            return m.class_
    return None

