import logging
from typing import Any, TypeVar

from slugify import slugify as base_slugify

T = TypeVar("T")


def cast_or_none(cast_to: type["T"], value: Any) -> T | None:
    if value:
        return cast_to(value)
    return None


logger = logging.getLogger(__name__)


def slugify(
    string: str,
    separator: str = "-",
    replacements: tuple[tuple[str, str]] = (
        ("+", " plus "),
        ("%", " pct "),
    ),
) -> str:
    slug = base_slugify(string, separator=separator, replacements=replacements)
    if not slug:
        logger.error("Can't slugify words: %s", string)
        return string
    return slug