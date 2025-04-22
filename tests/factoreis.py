from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory
from polyfactory.fields import Ignore

from netsight.features.admin.models import Group, Menu, Permission, Role, User
from netsight.features.admin.security import get_password_hash
from netsight.features.org import models as org_models
from netsight.features.org import schemas as org_schemas


class UserFactory(SQLAlchemyFactory[User]):
    __model__ = User
    __set_foreign_keys__ = False
    id = Ignore()
    password = get_password_hash("admin123")


class GroupFactory(SQLAlchemyFactory[Group]):
    __model__ = Group
    __set_foreign_keys__ = False
    id = Ignore()


class RoleFactory(SQLAlchemyFactory[Role]):
    __model__ = Role
    __set_foreign_keys__ = False
    id = Ignore()


class PermissionFactory(SQLAlchemyFactory[Permission]):
    __set_foreign_keys__ = False
    __model__ = Permission


class MenuFactory(SQLAlchemyFactory[Menu]):
    __model__ = Menu
    __set_foreign_keys__ = False
    id = Ignore()

    permission = [1, 2, 3, 4]  # noqa: RUF012


class SiteCreateFactory(ModelFactory[org_schemas.SiteCreate]):
    __model__ = org_schemas.SiteCreate


class SiteGroupCreateFactory(ModelFactory[org_schemas.SiteGroupCreate]):
    __model__ = org_schemas.SiteGroupCreate


class SiteFactory(SQLAlchemyFactory[org_models.Site]):
    __model__ = org_models.Site
    __set_foreign_keys__ = False
    id = Ignore()
    status = "Active"
    country = "China"
    time_zone = 8
