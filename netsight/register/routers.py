from fastapi import APIRouter

from netsight.features.admin.api import router as auth_router
from netsight.features.circuit.api import router as circuit_router
from netsight.features.dcim.api import router as dcim_router
from netsight.features.intend.api import router as intend_router
from netsight.features.ipam.api import router as ipam_router
from netsight.features.org.api import router as org_router


def register_router() -> APIRouter:
    root_router = APIRouter()
    root_router.include_router(auth_router, prefix="/admin", tags=["Administration"])
    root_router.include_router(org_router, prefix="/org", tags=["Organization"])
    root_router.include_router(intend_router, prefix="/intend", tags=["NetworkIntend"])
    root_router.include_router(dcim_router, prefix="/dcim", tags=["DCIM"])
    root_router.include_router(ipam_router, prefix="/ipam", tags=["IPAM"])
    root_router.include_router(circuit_router, prefix="/circuit", tags=["Circuit"])
    return root_router


router = register_router()
