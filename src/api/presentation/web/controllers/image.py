from typing import Annotated

from fastapi import Depends, File, Query, UploadFile
from faststream.nats import JStream, PullSub
from faststream.nats.fastapi import NatsBroker, NatsRouter
from pydantic import HttpUrl
from shared.messages import ImageProcessOutMessage
from shared.types import LanguageCode
from starlette import status

from api.application.exceptions.image import (
    ImageOneTypeError,
    RequestFileIsEmptyError,
    UnsupportedImageFormatError,
    UploadedImageError,
    UploadExceedSizeLimitError,
)
from api.application.image_saver import ImageSaveHelper
from api.application.services import TranslationImageService
from api.application.types import TranslationImageID
from api.infrastructure.database.holder import DatabaseHolder
from api.presentation.stub import Stub
from api.presentation.types import TranslationImageMeta
from api.presentation.upload_reader import UploadImageHandler
from api.presentation.web.controllers.schemas.responses.image import TranslationImageResponseSchema

router = NatsRouter(
    tags=["Images"],
)


@router.post(
    "/translations/upload_image",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": RequestFileIsEmptyError.message,
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "description": UnsupportedImageFormatError.message,
        },
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "description": UploadExceedSizeLimitError.message,
        },
    },
)
async def upload_image(
    broker: NatsBroker,
    title: str,
    number: Annotated[int | None, Query(gt=0)] = None,
    language: LanguageCode = LanguageCode.EN,
    is_draft: bool = False,
    image_file: Annotated[UploadFile, File(...)] = None,
    image_url: HttpUrl | None = None,
    *,
    db_holder: DatabaseHolder = Depends(Stub(DatabaseHolder)),
    upload_reader: UploadImageHandler = Depends(Stub(UploadImageHandler)),
    image_saver: ImageSaveHelper = Depends(Stub(ImageSaveHelper)),
) -> TranslationImageResponseSchema:
    if image_file and image_url:
        raise ImageOneTypeError
    elif image_file is None and image_url is None:
        raise UploadedImageError
    else:
        image_obj = (
            await upload_reader.read(image_file)
            if image_file
            else await upload_reader.download(str(image_url))
        )

    image_resp_dto = await TranslationImageService(
        db_holder=db_holder,
        image_saver=image_saver,
        broker=broker,
    ).create(
        meta=TranslationImageMeta(
            number=number,
            title=title,
            language=language,
            is_draft=is_draft,
        ),
        image=image_obj,
    )

    return TranslationImageResponseSchema(
        id=image_resp_dto.id,
        original=image_resp_dto.original_rel_path,
    )


@router.subscriber(
    "internal.api.images.process.out",
    queue="process_images_out_queue",
    stream=JStream(
        name="process_images_out_stream",
        max_age=600,
    ),
    pull_sub=PullSub(),
    durable="api",
)
async def processed_images_handler(
    msg: ImageProcessOutMessage,
    db_holder: DatabaseHolder = Depends(Stub(DatabaseHolder)),
    image_saver: ImageSaveHelper = Depends(Stub(ImageSaveHelper)),
):
    await TranslationImageService(
        db_holder=db_holder,
        image_saver=image_saver,
    ).update(
        image_id=TranslationImageID(msg.image_id),
        converted_abs_path=msg.converted_abs_path,
        thumbnail_abs_path=msg.thumbnail_abs_path,
    )
