from fastapi.requests import Request
from fastapi.security import OAuth2PasswordRequestForm
from sqladmin import ModelView
from sqladmin.authentication import AuthenticationBackend

from src.core.database.session import async_session
from src.core.utils.context import locale_ctx
from src.features.admin import models
from src.features.admin.security import generate_access_token_response
from src.features.admin.services import user_service
from src.features.deps import sqladmin_auth


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        form = await request.form()
        user_form = OAuth2PasswordRequestForm(username=form["username"], password=form["password"])
        async with async_session() as session:
            user = await user_service.verify_user(session, user_form)
        token = generate_access_token_response(user.id)
        request.session.update({"Authorization": f"Bearer {token.access_token}"})
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> bool:
        token = request.session.get("Authorization")
        if not token or "Bearer " not in token:
            return False
        token = token.split("Bearer ")[1]
        await sqladmin_auth(token)
        return True


class UserView(ModelView, model=models.User):
    name = models.User.__visible_name__[locale_ctx.get()]

    column_list = [
        models.User.id,
        models.User.name,
        models.User.email,
        models.User.phone,
        models.User.avatar,
        models.User.last_login,
        models.User.is_active,
        models.User.group,
        models.User.role,
        models.User.last_login,
        models.User.created_at,
        models.User.updated_at,
    ]
    column_searchable_list = [models.User.email, models.User.phone]
    column_filters = [models.User.email, models.User.phone]

    page_size = 20
    page_size_options = [20, 50, 100, 200]

    form_ajax_refs = {"group": {"fields": ("name",), "order_by": "id"}, "role": {"fields": ("name",), "order_by": "id"}}


class GroupView(ModelView, model=models.Group):
    name = models.Group.__visible_name__[locale_ctx.get()]

    column_list = [
        models.Group.id,
        models.Group.name,
        models.Group.description,
        models.Group.role,
        models.Group.user_count,
        models.Group.created_at,
        models.Group.updated_at,
    ]
    column_searchable_list = [models.Group.name]
    column_filters = [models.Group.name]

    page_size = 20
    page_size_options = [20, 50, 100, 200]

    form_ajax_refs = {"role": {"fields": ("name",), "order_by": "id"}}


class RoleView(ModelView, model=models.Role):
    name = models.Role.__visible_name__[locale_ctx.get()]

    column_list = [
        models.Role.id,
        models.Role.name,
        models.Role.description,
        models.Role.permission_count,
        models.Role.user_count,
        models.Role.created_at,
        models.Role.updated_at,
    ]
    column_searchable_list = [models.Role.name]
    column_filters = [models.Role.name]

    page_size = 20
    page_size_options = [20, 50, 100, 200]

    form_ajax_refs = {"group": {"fields": ("name",), "order_by": "id"}}
