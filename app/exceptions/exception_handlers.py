import logging

from fastapi import Request, HTTPException

from starlette.exceptions import HTTPException as StarletteHTTPException
from app.exceptions.custom_exceptions import CustomAPIError
from app.utils.error_codes import ErrorCodes
from app.utils.response_handler import error_response

logger = logging.getLogger(__name__)


async def global_exception_handler(request: Request, exc: Exception):
    return await error_response(
        status_code=ErrorCodes.INTERNAL_SERVER_ERROR.value,
        error_code=ErrorCodes.INTERNAL_SERVER_ERROR,
        message="An unexpected internal server error occurred",
    )


async def http_exception_handler(request: Request, exc: HTTPException):
    """
    triggered by FastAPI HTTPException when is raised inside endpoints
    """

    return await error_response(
        status_code=exc.status_code,
        error_code=ErrorCodes(exc.status_code),
        message=exc.detail,
    )


async def custom_api_exception_handler(request: Request, exc: CustomAPIError):
    return await error_response(
        error_code=ErrorCodes(exc.error_code),
        message=exc.message,
        status_code=exc.status_code,
    )


async def starlette_http_exception_handler(
    request: Request, exc: StarletteHTTPException
):
    error_code = (
        ErrorCodes(exc.status_code).value
        if exc.status_code in {e.value for e in ErrorCodes}
        else ErrorCodes.BAD_REQUEST.value
    )

    return await custom_api_exception_handler(
        request,
        CustomAPIError(
            status_code=exc.status_code,
            error_code=error_code,
            message=exc.detail or "An HTTP error occurred",
        ),
    )
