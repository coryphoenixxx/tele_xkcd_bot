import datetime
from dataclasses import dataclass
from enum import StrEnum
from typing import Annotated, NewType

from annotated_types import Ge
from shared.my_types import Order

from api.my_types import Tag

Limit = NewType("Limit", Annotated[int, Ge(0)])
Offset = NewType("Offset", Annotated[int, Ge(0)])


class TagParam(StrEnum):
    AND = "AND"
    OR = "OR"


@dataclass(slots=True)
class DateRange:
    start: datetime.date | None
    end: datetime.date | None


@dataclass(slots=True)
class ComicFilterParams:
    q: str | None
    limit: Limit | None
    offset: Offset | None
    date_range: DateRange | None
    order: Order | None
    tags: list[Tag] | None
    tag_param: TagParam | None
