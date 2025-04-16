import logging
from typing import Any, Optional

import httpx

from app.core.settings.config import get_config

logger = logging.getLogger(__name__)


class DiscordClient:
    def __init__(self):
        self.base_url = get_config().DISCORD_WEBHOOK_URL

    async def post(self, data: Optional[dict[str, Any]] = None) -> Any:
        return await self._request("POST", json=data)

    async def _request(
        self,
        method: str,
        json: Optional[dict[str, Any]] = None,
    ) -> Any:
        httpx_logger = logging.getLogger("httpx")
        original_level = httpx_logger.level
        httpx_logger.setLevel(logging.WARNING)

        try:
            async with httpx.AsyncClient(timeout=30) as client:
                response = await client.request(
                    method=method,
                    url=self.base_url,
                    json=json,
                )
                response.raise_for_status()
                return response.status_code in (200, 204)

        except httpx.HTTPStatusError as e:
            logger.warning(f"HTTP error {e.response.status_code}: {e.response.text}")
        except httpx.RequestError as e:
            logger.warning(f"Network error: {str(e)}")
        except Exception as e:
            logger.warning(f"Unhandled DiscordClient error: {str(e)}")

        finally:
            httpx_logger.setLevel(original_level)

        return False


class DiscordOperations:
    def __init__(self, client: Optional[DiscordClient] = None):
        self.client = client or DiscordClient()

    async def send_discord_message(
        self,
        message: str,
        job_name: Optional[str] = None,
        is_critical: bool = False,
        mention_everyone: bool = False,
    ):
        prefix = "❌ [CRITICAL]" if is_critical else ""
        job_tag = f"[{job_name}] " if job_name else ""
        alert = "@everyone " if mention_everyone else ""
        content = f"{alert}{prefix} {job_tag}{message}"
        payload = {"content": content}
        return await self.client.post(data=payload)


def get_discord_operations() -> DiscordOperations:
    return DiscordOperations()
