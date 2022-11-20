from fastapi import APIRouter

from src.api.auth import views


def register_router():
    root_router = APIRouter()
    root_router.include_router(views.router, prefix="/auth", tags=["Auth"])

    return root_router


router = register_router()
