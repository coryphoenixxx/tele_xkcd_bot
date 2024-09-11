from collections.abc import Sequence
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.interfaces import ORMOption

from backend.infrastructure.database.models import BaseModel

Model = TypeVar("Model", bound=BaseModel)


class RepoError(Exception): ...


class BaseRepo:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_model_by_id(
        self,
        model: type[Model],
        id_: int,
        *,
        options: ORMOption | Sequence[ORMOption] | None = None,
    ) -> Model | None:
        return await self._session.get(
            model,
            id_,
            options=(options,) if isinstance(options, ORMOption) else options,
        )
