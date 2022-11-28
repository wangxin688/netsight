ADMIN_BLACK_LIST = {"/api/v1/auth/user-tokens": "POST"}

USER_WHITE_LIST = {
    "/api/v1/auth/login": "POST",
    "/api/v1/auth/lark-login": "POST",
    "/api/v1/auth/register": "POST",
    "/api/v1/auth/refresh-token": "POST",
}

METHOD = ("PUT", "POST", "GET", "DELETE", "PATCH")
