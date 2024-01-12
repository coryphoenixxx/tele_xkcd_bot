# ruff: noqa: F401

import asyncio

from alembic import context

# noinspection PyUnresolvedReferences
from src.app.comics.models import ComicModel, ComicTagAssociation, TagModel

# noinspection PyUnresolvedReferences
from src.app.images.models import TranslationImageModel

# noinspection PyUnresolvedReferences
from src.app.translations.models import TranslationModel
from src.core.database import create_engine
from src.core.database.base import Base
from src.core.settings import get_settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
# Interpret the config file for Python logging.
# This line sets up loggers basically.
# if config.config_file_name is not None:
#     fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata


# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations():
    """In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    engine = create_engine(config=get_settings().db)

    async with engine.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await engine.dispose()


def run_migrations_online():
    """Run migrations in 'online' mode."""

    asyncio.run(run_async_migrations())


run_migrations_online()