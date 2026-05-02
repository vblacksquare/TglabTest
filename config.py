
from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class Django(BaseModel):
    secret_key: str
    allowed_hosts: list[str]

    email_host: str
    email_port: int
    email_use_tls: bool
    email_host_user: str
    email_host_password: str

    admin_name: str
    admin_email: str
    admin_password: str


class Database(BaseModel):
    name: str
    user: str
    password: str
    host: str


class Settings(BaseSettings):
    django: Django
    database: Database

    model_config = SettingsConfigDict(
        env_file=f".env",
        case_sensitive=False,
        env_nested_delimiter="__",
    )


@lru_cache(maxsize=1)
def get_config() -> Settings:
    return Settings()
