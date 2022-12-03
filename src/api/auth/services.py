import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncResult
from sqlalchemy.orm import selectinload

from src.api.auth.models import Role
from src.db.db_session import async_session


def url_match(path: str, method: str, permissions: dict) -> bool:
    if permissions.get(path) and permissions.get(path) == method:
        return True
    for key, value in permissions.items():
        reg = "^%s$" % key
        if re.match(reg, path) and method == value:
            return True
    return False


async def permission_dict_generate():
    result = {}
    async with async_session() as session:
        res: AsyncResult = session.execute(
            select(Role).options(selectinload(Role.auth_permission))
        )
        await res.scalars()
        for role in res.scalars():
            permissions = role.auth_permission
            result.update(
                {
                    role.name: {
                        permission.url: permission.action for permission in permissions
                    }
                }
            )
    return result
