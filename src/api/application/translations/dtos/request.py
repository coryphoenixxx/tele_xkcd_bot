from dataclasses import dataclass

from api.application.comics.types import ComicID
from api.application.images.types import TranslationImageID
from api.core.types import Language


@dataclass(slots=True)
class TranslationRequestDTO:
    comic_id: ComicID | None
    title: str
    language: Language
    tooltip: str | None
    transcript: str | None
    images: list[TranslationImageID]
    is_draft: bool