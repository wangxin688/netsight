from typing import Literal

DURATION = Literal[
    "1 month",
    "3 months",
    "6 months",
    "12 months",
    "3 years",
]

DURATION_MAPPING = {
    "1 month": 30 * 24 * 3600,
    "3 months": 30 * 24 * 3600 * 3,
    "6 months": 30 * 24 * 3600 * 6,
    "12 months": 30 * 24 * 3600 * 12,
    "3 years": 30 * 24 * 3600 * 36,
}

ADMIN_BLACK_LIST = {"/api/v1/auth/user-tokens": "POST"}

USER_WHITE_LIST = {
    "/api/v1/auth/login": "POST",
    "/api/v1/auth/lark-login": "POST",
    "/api/v1/auth/register": "POST",
    "/api/v1/auth/refresh-token": "POST",
}

METHOD = {"PUT", "POST", "GET", "DELETE", "PATCH"}
