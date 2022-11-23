import json

from src.core.config import settings
from src.utils.extensions.async_requests import async_http_req

LARK_URL = settings.LARK_URL


class LarkClient:
    def __init__(self, token: str) -> None:
        self.url = LARK_URL
        self.token = token
        self.headers = {
            "Authorization": "Bearer " + self.token,
            "Content-Type": "application/json; charset=utf-8",
        }

    async def get_user_identity(self, code: str):
        self.url + "/open-apis/authen/v1/access_token"
        data = {"grant_type": "authorization_code", "code": code}
        result = await async_http_req(
            "post", headers=self.headers, data=json.dumps(data)
        )
        return result
