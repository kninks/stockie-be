from fastapi import Security, Depends
from fastapi.security.api_key import APIKeyHeader

from app.config import config
from app.exceptions.custom_exceptions import AuthError, ForbiddenError

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


async def verify_api_key(api_key: str = Security(api_key_header)):
    if not api_key:
        raise AuthError("API Key missing")

    for role, key in config.ALLOWED_API_KEYS.items():
        if api_key == key:
            return role

    raise AuthError("Invalid API Key")


def verify_role(allowed_roles: list[str]):
    async def role_checker(user_role: str = Depends(verify_api_key)):
        if user_role not in allowed_roles:
            raise ForbiddenError("Unauthorized access")
        return user_role

    return role_checker
