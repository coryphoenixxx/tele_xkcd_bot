from collections.abc import AsyncIterable

from dishka import Provider, Scope, provide
from shared.config_loader import load_config
from shared.http_client import AsyncHttpClient
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
)

from api.application.image_saver import ImageSaveHelper
from api.application.services import ComicService, TranslationImageService, TranslationService
from api.config import APIConfig
from api.infrastructure.database import (
    ComicGateway,
    DbConfig,
    TranslationGateway,
    TranslationImageGateway,
    UnitOfWork,
    check_db_connection,
    create_db_engine,
    create_db_session_factory,
)
from api.presentation.upload_reader import UploadImageHandler


class ConfigsProvider(Provider):
    @provide(scope=Scope.APP)
    def db_config(self) -> DbConfig:
        return load_config(DbConfig, scope="db")

    @provide(scope=Scope.APP)
    def api_config(self) -> APIConfig:
        return load_config(APIConfig, scope="api")


class DbProvider(Provider):
    @provide(scope=Scope.APP)
    async def db_engine(self, config: DbConfig) -> AsyncIterable[AsyncEngine]:
        engine = create_db_engine(config)

        await check_db_connection(engine)

        yield engine
        await engine.dispose()

    @provide(scope=Scope.APP)
    def db_session_pool(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        return create_db_session_factory(engine)

    @provide(scope=Scope.REQUEST)
    async def db_session(
        self,
        session_pool: async_sessionmaker[AsyncSession],
    ) -> AsyncIterable[AsyncSession]:
        async with session_pool() as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def uow(self, session: AsyncSession) -> AsyncIterable[UnitOfWork]:
        async with UnitOfWork(session) as uow:
            yield uow


class HelpersProvider(Provider):
    @provide(scope=Scope.APP)
    async def async_http_client(self) -> AsyncIterable[AsyncHttpClient]:
        async with AsyncHttpClient() as client:
            yield client

    @provide(scope=Scope.REQUEST)
    def upload_image_handler(
        self,
        config: APIConfig,
        http_client: AsyncHttpClient,
    ) -> UploadImageHandler:
        return UploadImageHandler(config, http_client)

    image_save_helper = provide(ImageSaveHelper, scope=Scope.REQUEST)


class GatewaysProvider(Provider):
    scope = Scope.REQUEST

    comic_gateway = provide(ComicGateway)
    translation_gateway = provide(TranslationGateway)
    translation_image_gateway = provide(TranslationImageGateway)


class ServicesProvider(Provider):
    scope = Scope.REQUEST

    comic_service = provide(ComicService)
    translation_service = provide(TranslationService)
    translation_image_service = provide(TranslationImageService)