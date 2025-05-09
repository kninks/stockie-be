import logging
from typing import Any, Awaitable, Callable

from app.api.ml_ops.schemas.inference_schema import StockToPredictRequestSchema
from app.core.clients.ml_server_client import MLServerClient
from app.core.common.exceptions.custom_exceptions import MLServerError

logger = logging.getLogger(__name__)


class MLServerOperations:
    def __init__(self, client: MLServerClient):
        self.client = client

    @staticmethod
    async def _make_request(
        func: Callable[..., Awaitable[Any]],
        *args,
        error_message: str = "Backend request failed",
        **kwargs,
    ) -> Any:
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logger.error(f"{error_message}: {str(e)}")
            raise MLServerError(f"{error_message}: {str(e)}")

    async def run_inference(
        self, stocks: list[StockToPredictRequestSchema], days_ahead: int
    ) -> Any:
        payload = {
            "stocks": [stock.model_dump() for stock in stocks],
            "days_ahead": days_ahead,
        }
        return await self._make_request(
            self.client.post,
            "/predict",
            data=payload,
            error_message="Failed to trigger inference",
        )


def get_ml_server_operations() -> MLServerOperations:
    return MLServerOperations(client=MLServerClient())
