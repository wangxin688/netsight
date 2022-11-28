import multiprocessing
from pathlib import Path
from typing import Literal

import toml
from pydantic import AnyHttpUrl, BaseSettings, EmailStr, PostgresDsn, validator

PROJECT_DIR = Path(__file__).parent.parent.parent
PYPROJECT_CONTENT = toml.load(f"{PROJECT_DIR}/pyproject.toml")["tool"]["poetry"]


class Settings(BaseSettings):
    # CORE SETTINGS
    SECRET_KEY: str
    ENVIRONMENT: Literal["DEV", "PYTEST", "STG", "PRD"] = "DEV"
    SECURITY_BCRYPT_ROUNDS: int = 12
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 11520  # 8 days
    REFRESH_TOKEN_EXPIRE_MINUTES: int = 40320  # 28 days
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    ALLOWED_HOSTS: list[str] = ["localhost"]
    LOG_LEVEL: Literal["DEBUG", "INFO", "ERROR"] = "INFO"
    ENABLE_JSON_LOG: bool = "False"
    JSON_LOGS: bool = False
    WORKERS: int = multiprocessing.cpu_count() * 2

    # PROJECT NAME, VERSION AND DESCRIPTION
    PROJECT_NAME: str = PYPROJECT_CONTENT["name"]
    VERSION: str = PYPROJECT_CONTENT["version"]
    DESCRIPTION: str = PYPROJECT_CONTENT["description"]
    LOG_DIR: str = f"{PROJECT_DIR}/log/netsight.log"
    MAJAR_VERSION: int = 1
    AUTH: Literal["Simple", "Lark"] = "Simple"

    # POSTGRESQL DEFAULT DATABASE
    DEFAULT_DATABASE_HOSTNAME: str
    DEFAULT_DATABASE_USER: str
    DEFAULT_DATABASE_PASSWORD: str
    DEFAULT_DATABASE_PORT: str
    DEFAULT_DATABASE_DB: str
    SQLALCHEMY_DATABASE_URI: str = ""

    # REDIS
    REDIS_HOST: str
    REDIS_PORT: str
    REDIS_PASSWORD: str

    # REDIS_DSN: str

    # # CELERY
    # BROKER_URL: AmqpDsn
    # RESULT_BACKEND: RedisDsn

    # FIRST SUPERUSER
    FIRST_SUPERUSER_NAME: str
    FIRST_SUPERUSER_EMAIL: EmailStr
    FIRST_SUPERUSER_PASSWORD: str

    LARK_URL: AnyHttpUrl

    @validator("SQLALCHEMY_DATABASE_URI")
    def _assemble_default_db_connection(cls, v: str, values: dict[str, str]) -> str:
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            user=values["DEFAULT_DATABASE_USER"],
            password=values["DEFAULT_DATABASE_PASSWORD"],
            host=values["DEFAULT_DATABASE_HOSTNAME"],
            port=values["DEFAULT_DATABASE_PORT"],
            path=f"/{values['DEFAULT_DATABASE_DB']}",
        )

    class Config:
        env_file = f"{PROJECT_DIR}/.env"
        case_sensitive = True


settings = Settings()
