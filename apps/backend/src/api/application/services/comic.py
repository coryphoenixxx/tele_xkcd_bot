from shared.my_types import Order

from api.application.dtos.common import ComicFilterParams, Limit, TotalCount
from api.application.dtos.requests import ComicRequestDTO
from api.application.dtos.responses import (
    ComicResponseDTO,
    ComicResponseWTranslationsDTO,
)
from api.core.entities import ComicID, IssueNumber
from api.infrastructure.database.gateways import ComicGateway
from api.infrastructure.database.uow import UnitOfWork


class ComicService:
    def __init__(self, uow: UnitOfWork, gateway: ComicGateway) -> None:
        self._uow = uow
        self._gateway = gateway

    async def create(self, comic_req_dto: ComicRequestDTO) -> ComicResponseDTO:
        comic_resp_dto = await self._gateway.create(comic_req_dto)

        await self._uow.commit()

        return comic_resp_dto

    async def update(self, comic_id: ComicID, comic_req_dto: ComicRequestDTO) -> ComicResponseDTO:
        comic_resp_dto = await self._gateway.update(comic_id, comic_req_dto)
        await self._uow.commit()

        return comic_resp_dto

    async def delete(self, comic_id: ComicID) -> None:
        await self._gateway.delete(comic_id)

        await self._uow.commit()

    async def get_by_id(self, comic_id: ComicID) -> ComicResponseWTranslationsDTO:
        return await self._gateway.get_by_id(comic_id)

    async def get_by_issue_number(self, number: IssueNumber) -> ComicResponseWTranslationsDTO:
        return await self._gateway.get_by_issue_number(number)

    async def get_by_slug(self, slug: str) -> ComicResponseWTranslationsDTO:
        return await self._gateway.get_by_slug(slug)

    async def get_latest_issue_number(self) -> IssueNumber:
        return (
            await self._gateway.get_list(
                filter_params=ComicFilterParams(
                    limit=Limit(1),
                    order=Order.DESC,
                )
            )
        )[1][0].number

    async def get_list(
        self,
        query_params: ComicFilterParams,
    ) -> tuple[TotalCount, list[ComicResponseWTranslationsDTO]]:
        total, comic_resp_dtos = await self._gateway.get_list(query_params)

        return total, comic_resp_dtos
