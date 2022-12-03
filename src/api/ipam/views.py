from fastapi_utils.inferring_router import InferringRouter

from src.register.middleware import AuditRoute

router = InferringRouter(route_class=AuditRoute)
