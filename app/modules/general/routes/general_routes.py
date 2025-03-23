import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import (
    ForbiddenError,
    ResourceNotFoundError,
)
from app.core.common.utils.error_codes import ErrorCodes
from app.core.common.utils.response_handlers import error_response, success_response
from app.core.dependencies.api_key_auth import verify_role
from app.core.dependencies.get_db import get_db
from app.core.enums.roles_enum import RoleEnum

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/general",
    tags=["General"],
)


@router.get("/health")
async def health_check(
    user_role: str = Depends(verify_role([RoleEnum.ML_SERVER.value])),
):
    return await success_response(
        message="Backend is healthy", data={"role": user_role}
    )


@router.get("/success-response")
async def test_success_response():
    logger.info("Test success response")
    return await success_response(data={"msg": "Test OK!"})


@router.get("/error-response")
async def test_error():
    return error_response(
        error_code=ErrorCodes.GENERIC_ERROR, message="Something went wrong!"
    )


@router.get("/log")
async def test_log():
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")
    return await success_response()


@router.get("/db")
async def test_db_endpoint(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT 1"))
    return {"test_result": result.scalar()}


@router.get("/client-protected")
async def client_protected(user_role: str = Depends(verify_role(["client"]))):
    return await success_response(
        message="Client-only endpoint accessed!", data={"role": user_role}
    )


@router.get("/ml-protected")
async def ml_protected(
    user_role: str = Depends(verify_role([RoleEnum.ML_SERVER.value])),
):
    return await success_response(
        message="ML Server-only endpoint accessed!", data={"role": user_role}
    )


@router.get("/api-keys")
async def test_missing_api_key(
    user_role: str = Depends(verify_role(["client", "ml_server"]))
):
    return await success_response(message="You should not see this")


@router.get("/test-internal-error")
async def test_internal_error():
    """Raises a general exception (will be caught by `global_exception_handler`)."""
    raise Exception("Unexpected failure")


@router.get("/test-http-exception")
async def test_http_exception():
    """Raises a standard HTTPException (expected error in an endpoint)."""
    raise HTTPException(status_code=403, detail="Forbidden resource")


@router.get("/test-custom-exception")
async def test_custom_exception():
    """Raises a custom API exception."""
    raise ForbiddenError("Custom exception called")


@router.get("/test-not-found")
async def test_not_found():
    """Raises a custom 'Resource Not Found' error."""
    raise ResourceNotFoundError("User")
