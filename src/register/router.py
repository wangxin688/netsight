from fastapi import APIRouter

from src.api.auth import auth_views


def register_router():
    root_router = APIRouter()
    root_router.include_router(auth_views.router, prefix="/auth", tags=["Auth"])

    return root_router


router = register_router()
