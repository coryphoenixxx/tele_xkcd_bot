from dataclasses import dataclass
from datetime import datetime as dt

from api.application.dtos.responses import (
    TranslationImageProcessedResponseDTO,
    TranslationResponseDTO,
)
from api.infrastructure.database.models import ComicModel
from api.types import ComicID, IssueNumber, Language, TranslationID


@dataclass(slots=True)
class ComicResponseDTO:
    id: ComicID
    number: IssueNumber | None
    publication_date: dt.date
    explain_url: str | None
    link_on_click: str | None
    is_interactive: bool
    tags: list[str]
    translation_langs: list[Language]

    translation_id: TranslationID
    xkcd_url: str | None
    title: str
    tooltip: str
    images: list[TranslationImageProcessedResponseDTO]

    @classmethod
    def from_model(cls, model: ComicModel) -> "ComicResponseDTO":
        return ComicResponseDTO(
            id=model.comic_id,
            number=model.number,
            title=model.base_translation.title,
            translation_id=model.base_translation.translation_id,
            publication_date=model.publication_date,
            tooltip=model.base_translation.tooltip,
            xkcd_url=model.base_translation.source_link,
            explain_url=model.explain_url,
            link_on_click=model.link_on_click,
            is_interactive=model.is_interactive,
            tags=sorted([tag.name for tag in model.tags]),  # TODO: sort by SQL?
            images=[
                TranslationImageProcessedResponseDTO.from_model(img)
                for img in model.base_translation.images
            ],
            translation_langs=[tr.language for tr in model.translations],
        )


@dataclass(slots=True)
class ComicResponseWTranslationsDTO(ComicResponseDTO):
    translations: list[TranslationResponseDTO]

    @classmethod
    def from_model(cls, model: ComicModel) -> "ComicResponseWTranslationsDTO":
        return ComicResponseWTranslationsDTO(
            id=model.comic_id,
            number=model.number,
            title=model.base_translation.title,
            translation_id=model.base_translation.translation_id,
            publication_date=model.publication_date,
            tooltip=model.base_translation.tooltip,
            xkcd_url=model.base_translation.source_link,
            explain_url=model.explain_url,
            link_on_click=model.link_on_click,
            is_interactive=model.is_interactive,
            tags=sorted([tag.name for tag in model.tags]),
            images=[
                TranslationImageProcessedResponseDTO.from_model(img)
                for img in model.base_translation.images
            ],
            translation_langs=[tr.language for tr in model.translations],
            translations=[TranslationResponseDTO.from_model(t) for t in model.translations],
        )