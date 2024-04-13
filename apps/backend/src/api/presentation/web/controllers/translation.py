from fastapi import Depends
from faststream.nats.fastapi import NatsRouter as APIRouter
from starlette import status

from api.application.exceptions.comic import ComicByIDNotFoundError
from api.application.exceptions.translation import (
    EnglishTranslationOperationForbiddenError,
    ImagesAlreadyAttachedError,
    ImagesNotCreatedError,
    TranslationAlreadyExistsError,
    TranslationNotFoundError,
)
from api.application.services import TranslationService
from api.infrastructure.database.holder import DatabaseHolder
from api.presentation.stub import Stub
from api.presentation.web.controllers.schemas.requests import (
    TranslationDraftRequestSchema,
    TranslationRequestSchema,
)
from api.presentation.web.controllers.schemas.responses.translation import (
    TranslationWDraftStatusSchema,
    TranslationWLanguageResponseSchema,
)
from api.types import ComicID, TranslationID

router = APIRouter(tags=["Translations"])


@router.post(
    "/comics/{comic_id}/translations",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ComicByIDNotFoundError},
        status.HTTP_409_CONFLICT: {
            "model": TranslationAlreadyExistsError
            | ImagesNotCreatedError
            | ImagesAlreadyAttachedError,
        },
    },
)
async def add_translation(
    comic_id: ComicID,
    schema: TranslationRequestSchema,
    *,
    db_holder: DatabaseHolder = Depends(Stub(DatabaseHolder)),
) -> TranslationWLanguageResponseSchema:
    translation_resp_dto = await TranslationService(db_holder).add(comic_id, schema.to_dto())

    return TranslationWLanguageResponseSchema.from_dto(translation_resp_dto)


@router.post(
    "/comics/{comic_id}/translations/drafts",
    status_code=status.HTTP_201_CREATED,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": ComicByIDNotFoundError},
        status.HTTP_409_CONFLICT: {
            "model": ImagesNotCreatedError | ImagesAlreadyAttachedError,
        },
    },
)
async def add_translation_draft(
    comic_id: ComicID,
    schema: TranslationDraftRequestSchema,
    *,
    db_holder: DatabaseHolder = Depends(Stub(DatabaseHolder)),
) -> TranslationWLanguageResponseSchema:
    translation_resp_dto = await TranslationService(db_holder).add(comic_id, schema.to_dto())

    return TranslationWLanguageResponseSchema.from_dto(translation_resp_dto)


@router.put(
    "/translations/{translation_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": EnglishTranslationOperationForbiddenError},
        status.HTTP_404_NOT_FOUND: {"model": TranslationNotFoundError},
        status.HTTP_409_CONFLICT: {
            "model": ImagesNotCreatedError | ImagesAlreadyAttachedError,
        },
    },
)
async def update_translation(
    translation_id: TranslationID,
    schema: TranslationRequestSchema,
    *,
    db_holder: DatabaseHolder = Depends(Stub(DatabaseHolder)),
) -> TranslationWLanguageResponseSchema:
    translation_resp_dto = await TranslationService(db_holder).update(
        translation_id=translation_id,
        dto=schema.to_dto(),
    )

    return TranslationWLanguageResponseSchema.from_dto(translation_resp_dto)


@router.delete(
    "/translations/{translation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    responses={
        status.HTTP_400_BAD_REQUEST: {"model": EnglishTranslationOperationForbiddenError},
        status.HTTP_404_NOT_FOUND: {"model": TranslationNotFoundError},
    },
)
async def delete_translation(
    translation_id: TranslationID,
    *,
    db_holder: DatabaseHolder = Depends(Stub(DatabaseHolder)),
):
    await TranslationService(db_holder).delete(translation_id)


@router.get(
    "/translations/{translation_id}",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": TranslationNotFoundError},
    },
)
async def get_translation_by_id(
    translation_id: TranslationID,
    *,
    db_holder: DatabaseHolder = Depends(Stub(DatabaseHolder)),
) -> TranslationWDraftStatusSchema:
    translation_resp_dto = await TranslationService(db_holder).get_by_id(translation_id)

    return TranslationWDraftStatusSchema.from_dto(translation_resp_dto)


@router.get(
    "/translations/{translation_id}/raw_transcript",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": TranslationNotFoundError},
    },
)
async def get_translation_raw_transcript(
    translation_id: TranslationID,
    *,
    db_holder: DatabaseHolder = Depends(Stub(DatabaseHolder)),
) -> str:
    translation_resp_dto = await TranslationService(db_holder).get_by_id(translation_id)

    return translation_resp_dto.raw_transcript


@router.post(
    "/translations/{translation_id}/publish",
    status_code=status.HTTP_200_OK,
    responses={
        status.HTTP_404_NOT_FOUND: {"model": TranslationNotFoundError},
    },
)
async def publish_draft(
    translation_id: TranslationID,
    *,
    db_holder: DatabaseHolder = Depends(Stub(DatabaseHolder)),
):
    await TranslationService(db_holder).publish(translation_id)