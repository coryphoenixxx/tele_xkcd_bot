# mypy: disable-error-code="union-attr"

import re

from bs4 import BeautifulSoup
from rich.progress import Progress
from yarl import URL

from backend.infrastructure.downloader import Downloader
from backend.infrastructure.http_client import AsyncHttpClient
from backend.infrastructure.xkcd.pbar import CustomProgressBar
from backend.infrastructure.xkcd.scrapers import BaseScraper
from backend.infrastructure.xkcd.scrapers.dtos import LimitParams, XkcdTranslationScrapedData
from backend.infrastructure.xkcd.scrapers.exceptions import ExtractError, ScrapeError
from backend.infrastructure.xkcd.utils import run_concurrently

XKCD_NUMBER_PATTERN = re.compile(r".*xkcd.com/(.*)")


class XkcdESScraper(BaseScraper):
    _BASE_URL = URL("https://es.xkcd.com/")

    def __init__(self, client: AsyncHttpClient, downloader: Downloader) -> None:
        super().__init__(client=client, downloader=downloader)

    async def fetch_one(
        self,
        url: URL,
        range_: tuple[int, int],
    ) -> XkcdTranslationScrapedData | None:
        soup = await self._get_soup(url)

        number = self._extract_number(soup)

        if not number or number < range_[0] or number > range_[1]:
            return None

        try:
            translation_data = XkcdTranslationScrapedData(
                number=number,
                source_url=url,
                title=self._extract_title(soup),
                tooltip=self._extract_tooltip(soup),
                image_path=await self._downloader.download(url=self._extract_image_url(soup)),
                language="ES",
            )
            if translation_data.title == "Geografía":  # fix: https://es.xkcd.com/strips/geografia/
                translation_data.number = 1472
        except Exception as err:
            raise ScrapeError(url) from err
        else:
            return translation_data

    async def fetch_many(
        self,
        limits: LimitParams,
        progress: Progress,
    ) -> list[XkcdTranslationScrapedData]:
        return await run_concurrently(
            data=await self.fetch_all_links(),
            coro=self.fetch_one,
            chunk_size=limits.chunk_size,
            delay=limits.delay,
            pbar=CustomProgressBar(
                progress,
                f"Spanish translations scraping... \\[{self._BASE_URL}]",
            ),
            range_=(limits.start, limits.end),
        )

    async def fetch_all_links(self) -> list[URL]:
        url = self._BASE_URL / "archive/"
        soup = await self._get_soup(url)

        link_tags = soup.find("div", {"id": "archive-ul"}).find_all("a")

        return [self._BASE_URL / tag.get("href")[3:] for tag in link_tags]

    def _extract_number(self, soup: BeautifulSoup) -> int | None:
        xkcd_link = soup.find("div", {"id": "middleContent"}).find_all("a")[-1].get("href")

        if match := XKCD_NUMBER_PATTERN.match(xkcd_link):
            return int(match.group(1).replace("/", ""))
        return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        return soup.find("div", {"id": "middleContent"}).find("h1").text

    def _extract_tooltip(self, soup: BeautifulSoup) -> str:
        if tooltip := soup.find("img", {"class": "strip"}).get("title"):
            return str(tooltip)
        return ""

    def _extract_image_url(self, soup: BeautifulSoup) -> URL:
        if img_src := soup.find("img", {"class": "strip"}).get("src"):
            return self._BASE_URL / str(img_src)[6:]
        raise ExtractError
