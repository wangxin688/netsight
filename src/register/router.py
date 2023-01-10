from fastapi import APIRouter

from app.auth import api_auth, api_user
from app.circuit import api as circuit_views
from app.dcim import api as dcim_views
from app.ipam import api as ipam_views
from app.netsight import api as netsight_views


def register_router():
    root_router = APIRouter()
    root_router.include_router(api_auth.router, prefix="/auth", tags=["Auth"])
    root_router.include_router(api_user.router, prefix="/user", tags=["User"])
    root_router.include_router(
        netsight_views.router, prefix="/netsight", tags=["netsight"]
    )
    root_router.include_router(dcim_views.router, prefix="/dcim", tags=["DCIM"])
    root_router.include_router(
        circuit_views.router, prefix="/circuit", tags=["circuit"]
    )
    root_router.include_router(ipam_views.router, prefix="/ipam", tags=["ipam"])

    return root_router


router = register_router()
