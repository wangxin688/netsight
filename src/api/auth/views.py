from fastapi import APIRouter
from fastapi.responses import ORJSONResponse

auth_router = APIRouter(default_response_class=ORJSONResponse)


@auth_router.post("/login")
def login():
    pass
