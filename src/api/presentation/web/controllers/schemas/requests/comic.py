import datetime as dt

from pydantic import PositiveInt, HttpUrl, field_validator, BaseModel

from api.application.dtos.requests.comic import ComicRequestDTO
from api.application.dtos.requests.translation import TranslationRequestDTO
from api.application.types import TranslationImageID
from shared.types import (
    LanguageCode,
)
from shared.utils import cast_or_none


class ComicRequestSchema(BaseModel):
    number: PositiveInt | None
    publication_date: dt.date
    xkcd_url: HttpUrl | None
    explain_url: HttpUrl
    link_on_click: HttpUrl | None
    is_interactive: bool
    tags: list[str]

    def to_dto(self) -> ComicRequestDTO:
        return ComicRequestDTO(
            number=self.number,
            publication_date=self.publication_date,
            xkcd_url=cast_or_none(str, self.xkcd_url),
            explain_url=cast_or_none(str, self.explain_url),
            link_on_click=cast_or_none(str, self.link_on_click),
            is_interactive=self.is_interactive,
            tags=self.tags,
        )


class ComicWithEnTranslationRequestSchema(ComicRequestSchema):
    en_title: str
    en_tooltip: str
    en_transcript: str
    images: list[int]

    @field_validator("tags")
    @classmethod
    def validate_tags(cls, tags: list[str]) -> list[str] | None:
        if tags:
            for tag in tags:
                if not tag.strip() or len(tag) < 2:
                    raise ValueError(f"{tag} is invalid.")
        return list({tag.strip() for tag in tags})

    def to_dtos(self) -> tuple[ComicRequestDTO, TranslationRequestDTO]:
        return (
            ComicRequestDTO(
                number=self.number,
                publication_date=self.publication_date,
                xkcd_url=cast_or_none(str, self.xkcd_url),
                explain_url=cast_or_none(str, self.explain_url),
                link_on_click=cast_or_none(str, self.link_on_click),
                is_interactive=self.is_interactive,
                tags=self.tags,
            ),
            TranslationRequestDTO(
                comic_id=None,
                title=self.en_title,
                language=LanguageCode.EN,
                tooltip=self.en_tooltip,
                transcript=self.en_transcript,
                images=[TranslationImageID(image_id) for image_id in self.images],
                is_draft=False,
            ),
        )