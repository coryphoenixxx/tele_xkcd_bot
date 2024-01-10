from typing import Annotated

from fastapi import APIRouter, Depends, File, Query, UploadFile
from starlette import status

from src.app.comics.images.utils import ImageFileSaver, UploadImageReader
from src.app.dependency_stubs import DatabaseHolderDep, ImageFileSaverDep, UploadImageReaderDep
from src.core.database import DatabaseHolder
from src.core.types import Language

from .dtos import TranslationImageCreateDTO
from .exceptions import (
    RequestFileIsEmptyError,
    UnsupportedImageFormatError,
    UploadExceedLimitError,
)
from .services import TranslationImageService
from .types import TranslationImageID, TranslationImageVersion

router = APIRouter(
    tags=["Images"],
)


@router.post(
    "/comics/upload_image",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_400_BAD_REQUEST: {
            "description": RequestFileIsEmptyError.message,
        },
        status.HTTP_415_UNSUPPORTED_MEDIA_TYPE: {
            "description": UnsupportedImageFormatError.message,
        },
        status.HTTP_413_REQUEST_ENTITY_TOO_LARGE: {
            "description": UploadExceedLimitError.message,
        },
    },
)
async def upload_images(
    image: Annotated[UploadFile, File()],
    en_title: Annotated[str | None, Query(max_length=50)],
    issue_number: Annotated[int | None, Query(gt=0)] = None,
    language: Language = Language.EN,
    version: TranslationImageVersion = TranslationImageVersion.DEFAULT,
    is_draft: bool = False,
    db_holder: DatabaseHolder = Depends(DatabaseHolderDep),
    upload_reader: UploadImageReader = Depends(UploadImageReaderDep),
    image_saver: ImageFileSaver = Depends(ImageFileSaverDep),
) -> TranslationImageID:
    tmp_image_obj = await upload_reader.read(image)

    image_dto = TranslationImageCreateDTO(
        issue_number=issue_number,
        en_title=en_title,
        version=version,
        language=language,
        is_draft=is_draft,
        image=tmp_image_obj,
    )

    image_id = await TranslationImageService(
        db_holder=db_holder,
        image_saver=image_saver,
    ).create(image_dto)

    return image_id
