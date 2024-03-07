import logging
from pathlib import Path

from aiohttp import ClientConnectorError, ClientResponse  # noqa: F401
from scraper.dtos import (
    XkcdOriginUploadData,
    XkcdOriginWithExplainScrapedData,
    XkcdTranslationData,
    XkcdTranslationUploadData,
)
from scraper.pbar import ProgressBar
from yarl import URL

from shared.http_client import AsyncHttpClient
from shared.http_client.exceptions import HttpRequestError
from shared.types import (
    LanguageCode,
)


class APIRESTClient:
    _API_URL = URL("http://127.0.0.1:8000/api/")

    def __init__(self, client: AsyncHttpClient):
        self._client = client

    async def healthcheck(self) -> int | None:
        url = self._API_URL.joinpath("healthcheck")

        try:
            async with self._client.safe_get(url) as response:
                if response.status == 200:
                    return response.status
        except HttpRequestError:
            logging.fatal("API is offline or wrong API url.")

    async def create_comic_with_image(
        self,
        data: XkcdOriginWithExplainScrapedData,
        pbar: ProgressBar | None = None,
    ) -> dict[int, int]:
        images = []

        if data.image_url:
            image_id = (
                await self.upload_image(
                    title=data.title,
                    number=data.number,
                    language=LanguageCode.EN,
                    image_url=data.image_url,
                )
            )["id"]
            images.append(image_id)

        comic_id = await self.create_comic(
            comic=XkcdOriginUploadData(
                number=data.number,
                publication_date=data.publication_date,
                xkcd_url=data.xkcd_url,
                en_title=data.title,
                en_tooltip=data.tooltip,
                link_on_click=data.link_on_click,
                is_interactive=data.is_interactive,
                explain_url=data.explain_url,
                tags=data.tags,
                en_transcript_raw=data.transcript_raw,
                images=images,
            ),
        )

        if pbar:
            pbar.advance()

        return {data.number: comic_id}

    async def upload_image(
        self,
        title: str,
        number: int | None,
        language: LanguageCode,
        is_draft: bool = False,
        image_url: str | URL | None = None,
        image_path: Path | None = None,
    ) -> dict[str, int | str]:
        url = self._API_URL.joinpath("translations/upload_image")

        params = self._build_params(
            title=title,
            number=number,
            language=language,
            is_draft=is_draft,
            image_url=image_url,
        )

        async with self._client.safe_post(
            url=url,
            params=params,
            data={"image_file": open(image_path, "rb") if image_path else ""},
        ) as response:  # type:ClientResponse
            if response.status == 201:
                return await response.json()
            else:
                error_json = await response.json()
                print(error_json)

    async def create_comic(self, comic: XkcdOriginUploadData) -> int:
        url = self._API_URL.joinpath("comics")

        async with self._client.safe_post(
            url=url,
            json=comic,
        ) as response:  # type:ClientResponse
            if response.status == 201:
                return (await response.json())["id"]
            else:
                error_json = await response.json()
                print(error_json)

    async def add_translation_with_image(
        self,
        data: XkcdTranslationData,
        number_comic_id_map: dict[int, int],
        pbar: ProgressBar | None = None,
    ):
        url = self._API_URL.joinpath("translations")

        images = []

        comic_id = number_comic_id_map[data.number]

        if data.image:
            image_id = (
                await self.upload_image(
                    title=data.title,
                    number=data.number,
                    language=data.language,
                    image_url=data.image if isinstance(data.image, URL) else None,
                    image_path=data.image if isinstance(data.image, Path) else None,
                )
            )["id"]
            images.append(image_id)

        translation = XkcdTranslationUploadData(
            comic_id=comic_id,
            title=data.title,
            language=data.language,
            tooltip=data.tooltip,
            transcript_raw=data.transcript_raw,
            translator_comment=data.translator_comment,
            source_link=data.source_link,
            images=images,
        )

        async with self._client.safe_post(
            url=url,
            json=translation,
        ) as response:  # type:ClientResponse
            if response.status == 201:
                if pbar:
                    pbar.advance()
                return (await response.json())["id"]
            else:
                error_json = await response.json()
                print(error_json)

    async def get_comic_by_number(self, number: int):
        url = self._API_URL / f"comics/{number}"

        async with self._client.safe_get(url) as response:
            comic = await response.json()

        return comic

    @staticmethod
    def _build_params(**kwargs) -> dict[str, int | float | str]:
        params = {}
        for name, value in kwargs.items():
            if value is not None:
                params[name] = str(value)

        return params
