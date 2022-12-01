from fastapi import APIRouter

from src.api.auth import auth_views, user_views
from src.api.netsight import views as netsight_views


def register_router():
    root_router = APIRouter()
    root_router.include_router(auth_views.router, prefix="/auth", tags=["Auth"])
    root_router.include_router(user_views.router, prefix="/user", tags=["User"])
    root_router.include_router(
        netsight_views.router, prefix="/netsight", tags=["Netsight"]
    )

    return root_router


router = register_router()
