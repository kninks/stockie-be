from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.top_stock.schema.top_stock_api_schema import (
    TopStockRequestSchema,
    TopStockResponseSchema,
)
from app.modules.top_stock.services.top_stock_service import TopStockService


class TopStockController:
    @staticmethod
    async def get_top_stock_response(
        request: TopStockRequestSchema, db: AsyncSession
    ) -> TopStockResponseSchema:
        return await TopStockService().get_top_stock(request, db)
