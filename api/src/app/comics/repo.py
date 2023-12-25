from sqlalchemy import select, Sequence
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.strategy_options import joinedload

from src.app.comics.dtos import ComicCreateDTO

from .models import ComicModel, TagModel


class ComicRepo:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def create(self, comic_create_dto: ComicCreateDTO) -> int:
        tags = await self.add_tags(comic_create_dto.tags)

        comic_model = ComicModel(
            issue_number=comic_create_dto.issue_number,
            publication_date=comic_create_dto.publication_date,
            xkcd_url=comic_create_dto.xkcd_url,
            reddit_url=comic_create_dto.reddit_url,
            explain_url=comic_create_dto.explain_url,
            link_on_click=comic_create_dto.link_on_click,
            is_interactive=comic_create_dto.is_interactive,
            is_extra=comic_create_dto.is_extra,
            tags=tags,
        )

        self._session.add(comic_model)

        await self._session.flush()

        return comic_model.id

    async def get_by_id(self, comic_id: int):
        stmt = (
            select(ComicModel)
            .options(joinedload(ComicModel.translations), joinedload(ComicModel.tags))
            .where(ComicModel.id == comic_id)
        )
        return (await self._session.scalars(stmt)).unique().one_or_none()

    async def get_by_issue_number(self, issue_number: int):
        stmt = (
            select(ComicModel)
            .options(joinedload(ComicModel.translations), joinedload(ComicModel.tags))
            .where(ComicModel.issue_number == issue_number)
        )
        return (await self._session.scalars(stmt)).unique().one_or_none()

    async def add_tags(self, tags: list[str]) -> Sequence[TagModel]:
        input_tags = {TagModel(name=tag_name) for tag_name in tags}

        stmt = (
            insert(TagModel)
            .values([{"name": tag.name} for tag in input_tags])
            .on_conflict_do_nothing(
                constraint="uq_tags_name",
            )
        )

        await self._session.execute(stmt)

        stmt = select(TagModel).where(TagModel.name.in_((tag.name for tag in input_tags)))

        return (await self._session.scalars(stmt)).all()
