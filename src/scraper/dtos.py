from dataclasses import dataclass

from shared.types import LanguageCode
from yarl import URL


@dataclass(slots=True)
class XKCDOriginData:
    number: int
    publication_date: str
    xkcd_url: URL
    title: str
    tooltip: str
    link_on_click: URL | None
    is_interactive: bool
    image_url: URL | None


@dataclass(slots=True)
class XkcdTranslationData:
    number: int
    source_link: URL  # NEED?
    title: str
    tooltip: str | None
    image_url: URL | None
    transcript_html: str
    translator_comment: str


@dataclass(slots=True)
class XkcdTranslationPOSTData:
    comic_id: int
    title: str
    language: LanguageCode
    tooltip: str | None
    transcript_html: str
    translator_comment: str
    images: list[int]


@dataclass(slots=True)
class XKCDExplainData:
    explain_url: URL
    tags: list[str]
    transcript_html: str


@dataclass(slots=True)
class XKCDFullScrapedData:
    number: int
    publication_date: str
    xkcd_url: URL
    title: str
    tooltip: str
    link_on_click: URL | None
    is_interactive: bool
    image_url: URL | None
    explain_url: URL
    tags: list[str]
    transcript_html: str


@dataclass(slots=True)
class XKCDPOSTData:
    number: int
    publication_date: str
    xkcd_url: URL
    en_title: str
    en_tooltip: str
    link_on_click: URL | None
    is_interactive: bool
    explain_url: URL
    tags: list[str]
    en_transcript_html: str
    images: list[int]
