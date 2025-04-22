from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from netsight.core.database.types import DateTimeTZ


class AuditTimeMixin:
    created_at: Mapped[datetime] = mapped_column(DateTimeTZ, default=func.now(), index=True)
    updated_at: Mapped[datetime | None] = mapped_column(DateTimeTZ, onupdate=func.now())
