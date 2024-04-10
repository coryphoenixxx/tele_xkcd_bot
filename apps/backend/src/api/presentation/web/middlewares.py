import logging
from types import MappingProxyType

from fastapi.responses import ORJSONResponse
from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from api.application.exceptions.base import BaseAppError
from api.application.exceptions.comic import (
    ComicByIDNotFoundError,
    ComicByIssueNumberNotFoundError,
    ComicBySlugNotFoundError,
    ComicNumberAlreadyExistsError,
    ExtraComicTitleAlreadyExistsError,
)
from api.application.exceptions.image import (
    DownloadingImageError,
    RequestFileIsEmptyError,
    UnsupportedImageFormatError,
    UploadedImageError,
    UploadedImageTypeConflictError,
    UploadExceedSizeLimitError,
)
from api.application.exceptions.translation import (
    DraftForDraftCreationError,
    EnglishTranslationOperationForbiddenError,
    ImagesAlreadyAttachedError,
    ImagesNotCreatedError,
    TranslationAlreadyExistsError,
    TranslationNotFoundError,
)
from api.application.exceptions.user import InvalidCredentialsError, UsernameAlreadyExistsError

logger = logging.getLogger(__name__)

ERROR_TO_STATUS_MAP = MappingProxyType(
    {
        RequestFileIsEmptyError: status.HTTP_400_BAD_REQUEST,
        UploadedImageError: status.HTTP_400_BAD_REQUEST,
        DownloadingImageError: status.HTTP_400_BAD_REQUEST,
        UploadedImageTypeConflictError: status.HTTP_400_BAD_REQUEST,
        UploadExceedSizeLimitError: status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
        UnsupportedImageFormatError: status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
        ComicNumberAlreadyExistsError: status.HTTP_409_CONFLICT,
        ExtraComicTitleAlreadyExistsError: status.HTTP_409_CONFLICT,
        ImagesNotCreatedError: status.HTTP_400_BAD_REQUEST,
        ImagesAlreadyAttachedError: status.HTTP_400_BAD_REQUEST,
        ComicByIDNotFoundError: status.HTTP_404_NOT_FOUND,
        ComicByIssueNumberNotFoundError: status.HTTP_404_NOT_FOUND,
        ComicBySlugNotFoundError: status.HTTP_404_NOT_FOUND,
        TranslationAlreadyExistsError: status.HTTP_409_CONFLICT,
        TranslationNotFoundError: status.HTTP_404_NOT_FOUND,
        EnglishTranslationOperationForbiddenError: status.HTTP_400_BAD_REQUEST,
        UsernameAlreadyExistsError: status.HTTP_409_CONFLICT,
        InvalidCredentialsError: status.HTTP_401_UNAUTHORIZED,
        DraftForDraftCreationError: status.HTTP_400_BAD_REQUEST,
    },
)


class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        try:
            return await call_next(request)
        except BaseAppError as err:
            return ORJSONResponse(
                status_code=ERROR_TO_STATUS_MAP[err.__class__],
                content=err.detail,
            )
        except Exception as err:
            logger.error(err, exc_info=True)
            return ORJSONResponse(
                status_code=500,
                content={
                    "message": "An unexpected error occurred.",
                },
            )
