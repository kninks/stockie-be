import logging
from typing import Any, Optional

import httpx

from app.core.settings.config import config

logger = logging.getLogger(__name__)


class MLServerClient:
    def __init__(self):
        self.base_url = config.ML_SERVER_URL
        self.api_key = config.ML_SERVER_API_KEY
        self.headers = {"X-API-Key": self.api_key, "Content-Type": "application/json"}

    async def post(self, endpoint: str, data: Optional[dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url, json=data, headers=self.headers, timeout=30
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"ML Server error at {url}: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"Unexpected error contacting ML server at {url}: {str(e)}"
            )
            raise

    async def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
        url = f"{self.base_url}{endpoint}"
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url, params=params, headers=self.headers, timeout=30
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"ML Server error at {url}: {e.response.status_code} - {e.response.text}"
            )
            raise
        except Exception as e:
            logger.exception(
                f"Unexpected error contacting ML server at {url}: {str(e)}"
            )
            raise

    # async def get(self, endpoint: str, params: Optional[dict[str, Any]] = None) -> Any:
    #     url = f"{self.base_url}{endpoint}"
    # try:
    #     async with httpx.AsyncClient() as client:
    #         response = await client.get(
    #             url, params=params, headers=self.headers, timeout=30
    #         )
    #         response.raise_for_status()
    #
    #         json_data = response.json()
    #         if json_data.get("status") == "success":
    #             return json_data.get("data")
    #         else:
    #             raise Exception(f"ML server error: {json_data.get('message')}")
    #
    # except httpx.HTTPStatusError as e:
    #     logger.error(f"ML Server error at {url}: {e.response.status_code} - {e.response.text}")
    #     raise
    # except Exception as e:
    #     logger.exception(f"Unexpected error contacting ML server at {url}: {str(e)}")
    #     raise
