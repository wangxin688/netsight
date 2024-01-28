from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src import errors
from src._types import IdResponse, ListT
from src.auth import schemas
from src.auth.models import Group, Permission, Role, User
from src.auth.services import group_dto, menu_dto, role_dto, user_dto
from src.cbv import cbv
from src.deps import auth, get_session
from src.exceptions import GenerError
from src.security import generate_access_token_response
from src.validators import list_to_tree

router = APIRouter()


