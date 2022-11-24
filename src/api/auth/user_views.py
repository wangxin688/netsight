from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.auth import schemas
from src.api.auth.models import User
from src.api.base import BaseResponse
from src.api.deps import get_current_user, get_session
from src.register.middleware import AuditRoute

router = APIRouter(route_class=AuditRoute)


@router.post("users", response_model=BaseResponse[int])
async def create_user(
    user: schemas.UserCreate,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    pass
