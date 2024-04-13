from dataclasses import dataclass
from typing import Any

from api.application.exceptions.base import BaseAppError
from api.types import ComicID, IssueNumber


@dataclass
class ComicByIDNotFoundError(BaseAppError):
    comic_id: ComicID
    message: str = "A comic with this id not found."

    @property
    def detail(self) -> str | dict[str, Any]:
        return {
            "message": self.message,
            "comic_id": self.comic_id,
        }


@dataclass
class ComicByIssueNumberNotFoundError(BaseAppError):
    number: IssueNumber
    message: str = "A comic with this issue number not found."

    @property
    def detail(self) -> str | dict[str, Any]:
        return {
            "message": self.message,
            "number": self.number,
        }


@dataclass
class ComicNumberAlreadyExistsError(BaseAppError):
    number: IssueNumber
    message: str = "A comic with this issue number already exists."

    @property
    def detail(self) -> str | dict[str, Any]:
        return {
            "message": self.message,
            "number": self.number,
        }


@dataclass
class ComicBySlugNotFoundError(BaseAppError):
    slug: str
    message: str = "A comic with this slug not found."

    @property
    def detail(self) -> str | dict[str, Any]:
        return {
            "message": self.message,
            "slug": self.slug,
        }


@dataclass
class ExtraComicTitleAlreadyExistsError(BaseAppError):
    title: str
    message: str = "An extra comic with this title already exists."

    @property
    def detail(self) -> str | dict[str, Any]:
        return {
            "message": self.message,
            "title": self.title,
        }