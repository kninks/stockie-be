import logging

from fastapi.responses import JSONResponse
from app.utils.error_codes import ErrorCodes

logger = logging.getLogger(__name__)


async def success_response(
    data=None, message="Success", status_code=ErrorCodes.SUCCESS
):
    logger.info(f"Success | Status: {status_code.value} | Message: {message}")

    return JSONResponse(
        status_code=status_code.value,
        content={
            "status": "success",
            "message": message,
            "data": data,
        },
    )


async def error_response(
    error_code: ErrorCodes, message="An error occurred", status_code=None
):
    if not isinstance(error_code, ErrorCodes):
        logger.warning(
            f"Invalid error_code provided: {error_code}, defaulting to GENERIC_ERROR"
        )
        error_code = ErrorCodes.GENERIC_ERROR

    if status_code is None:
        status_code = error_code.value

    logger.error(
        f"Error | Code: {error_code.value} | Status: {status_code} | Message: {message}"
    )

    return JSONResponse(
        status_code=status_code,
        content={
            "status": "error",
            "message": message,
            "error_code": error_code.value,
        },
    )
