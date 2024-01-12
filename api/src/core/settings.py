from enum import StrEnum
from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class DBConfig(BaseModel):
    driver: str
    host: str
    port: int
    user: str
    password: str
    dbname: str

    @property
    def dsn(self):
        return f"postgresql+{self.driver}://{self.user}:{self.password}@{self.host}:{self.port}/{self.dbname}"


class SQLAConfig(BaseModel):
    pool_size: int = 10
    echo: bool = True


class DbConfig(BaseModel):
    pg: DBConfig
    sqla: SQLAConfig


class UvicornConfig(BaseModel):
    host: str = "localhost"
    port: int = 8000
    workers: int = 1
    reload: bool = True


class FastAPIConfig(BaseModel):
    docs_url: str = "/docs"
    redoc_url: str = "/redoc"
    openapi_url: str = "/openapi.json"
    debug: bool = True


class AppConfig(BaseModel):
    fastapi: FastAPIConfig = FastAPIConfig()
    upload_max_size: str
    tmp_dir: str
    static_dir: str


class Environment(StrEnum):
    DEV = "dev"
    PROD = "prod"


class Settings(BaseSettings):
    uvicorn: UvicornConfig
    db: DbConfig
    app: AppConfig
    env: Environment

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="__",
    )


@lru_cache
def get_settings():
    settings = Settings()
    if settings.env is Environment.PROD:
        settings.uvicorn.reload = False
        settings.db.sqla.echo = False
        settings.app.fastapi.docs_url = None
        settings.app.fastapi.redoc_url = None
        settings.app.fastapi.openapi_url = None
    return settings