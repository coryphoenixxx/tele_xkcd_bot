import asyncio
import logging
from pathlib import Path

import aiofiles.os as aos
import filetype
import imagesize
from aiofiles.tempfile import NamedTemporaryFile
from aiohttp import ClientPayloadError, StreamReader
from shared.http_client import AsyncHttpClient
from shared.my_types import HTTPStatusCodes, ImageFormat
from starlette.datastructures import UploadFile
from yarl import URL

from api.application.dtos.common import Dimensions, ImageObj
from api.application.exceptions.image import (
    DownloadingImageError,
    RequestFileIsEmptyError,
    UnsupportedImageFormatError,
    UploadExceedSizeLimitError,
)
from api.core.configs.web import APIConfig

logger = logging.getLogger(__name__)


class UploadImageHandler:
    _CHUNK_SIZE: int = 1024 * 64

    def __init__(
        self,
        config: APIConfig,
        http_client: AsyncHttpClient,
        download_timeout: float = 30.0,
    ) -> None:
        self._tmp_dir = config.tmp_dir
        self._upload_max_size = config.upload_max_size
        self._supported_formats = tuple(ImageFormat)
        self._http_client = http_client
        self._download_timeout = download_timeout

    async def read(self, upload: UploadFile | None) -> ImageObj:
        if not upload or not upload.filename:
            raise RequestFileIsEmptyError

        return await self._read_to_temp(upload)

    async def download(self, url: URL | str) -> ImageObj:
        try:
            return await asyncio.wait_for(self._download_job(url), self._download_timeout)
        except TimeoutError:
            logger.exception("Couldn't download %s after %s seconds.", url, self._download_timeout)
        raise DownloadingImageError(str(url))

    async def _download_job(self, url: URL | str) -> ImageObj | None:
        for _ in range(3):
            try:
                async with self._http_client.safe_get(url=url) as response:
                    if response.status == HTTPStatusCodes.HTTP_200_OK:
                        return await self._read_to_temp(response.content)
            except (TimeoutError, ClientPayloadError):
                await asyncio.sleep(1)
                continue

        return None  # TODO: что-то тут не то

    async def _read_to_temp(self, obj: StreamReader | UploadFile) -> ImageObj:
        await aos.makedirs(self._tmp_dir, exist_ok=True)

        try:
            async with NamedTemporaryFile(delete=False, dir=self._tmp_dir) as tmp:
                file_size = 0

                while chunk := await obj.read(self._CHUNK_SIZE):
                    file_size += len(chunk)

                    if file_size > self._upload_max_size:
                        raise UploadExceedSizeLimitError(upload_max_size=self._upload_max_size)

                    await tmp.write(chunk)

                if file_size == 0:
                    raise RequestFileIsEmptyError
        except Exception:
            await aos.remove(tmp.name)
            raise

        tmp_path = Path(tmp.name)

        return ImageObj(
            path=tmp_path,
            fmt=self._get_real_image_format(tmp_path),
            dimensions=Dimensions(*imagesize.get(tmp_path)),
        )

    def _get_real_image_format(self, path: Path) -> ImageFormat:
        # TODO: что-то тут не то
        fmt = None

        try:
            fmt = ImageFormat(filetype.guess_extension(path))
        except ValueError:
            raise UnsupportedImageFormatError(
                invalid_format=fmt,
                supported_formats=self._supported_formats,
            ) from None
        except FileNotFoundError as err:
            logging.exception("%s: %s", err.strerror, path)
            raise
        else:
            return fmt
