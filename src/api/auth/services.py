import re
from typing import List, Optional

from sqlalchemy import select

from src.api.auth.models import Permission, Role
from src.db.db_session import async_session


def url_match(path: str, method: str, permissions: dict) -> bool:
    if permissions.get(path) and permissions.get(path) == method:
        return True
    for key, value in permissions.items():
        reg = "^%s$" % key
        if all(re.match(reg, path), method == value):
            return True
    return False


async def permission_dict_generate():
    result = {}
    async with async_session() as session:
        roles: Optional[List[Role]] = (
            (await session.execute(select(Role))).scalars().all()
        )
        if roles:
            for role in roles:
                permissions: Optional[List[Permission]] = await role.auth_permission
                if permissions:
                    result.update(
                        {
                            role.name: {
                                permission.url: permission.action
                                for permission in permissions
                            }
                        }
                    )
    return result
