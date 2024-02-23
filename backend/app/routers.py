from fastapi import APIRouter

from app.arch.api import router as arch_router
from app.auth.api import router as auth_router
from app.circuit.api import router as circuit_router
from app.dcim.api import router as dcim_router
from app.ipam.api import router as ipam_router
from app.org.api import router as org_router


def register_router() -> APIRouter:
    root_router = APIRouter()
    root_router.include_router(auth_router, prefix="/auth", tags=["Auth"])
    root_router.include_router(dcim_router, prefix="/dcim", tags=["DCIM"])
    root_router.include_router(ipam_router, prefix="/ipam", tags=["IPAM"])
    root_router.include_router(arch_router, prefix="/arch", tags=["Architecture"])
    root_router.include_router(org_router, prefix="/org", tags=["Oganization"])
    root_router.include_router(circuit_router, prefix="/circuit", tags=["Circuit"])
    return root_router


router = register_router()
