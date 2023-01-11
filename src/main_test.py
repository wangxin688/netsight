from fastapi import FastAPI, Request
from fastapi_babel import _
from fastapi_babel.middleware import InternationalizationMiddleware

from src.utils.babel import babel

app = FastAPI()
app.add_middleware(InternationalizationMiddleware, babel=babel)


@app.get("/items/{id}")
async def read_item(request: Request, id: str):
    print(__file__)
    return id + _("internal server error")
