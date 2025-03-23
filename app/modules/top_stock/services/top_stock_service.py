from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import ResourceNotFoundError
from app.modules.top_stock.repositories.top_stock_repository import TopStockRepository
from app.modules.top_stock.schema.top_stock_api_schema import (
    OtherStockSchema,
    RecommendedStockSchema,
    TopStockRequestSchema,
    TopStockResponseSchema,
)


class TopStockService:

    def __init__(self):
        self.repository = TopStockRepository()

    async def get_top_stock(
        self, request: TopStockRequestSchema, db: AsyncSession
    ) -> TopStockResponseSchema:
        top_stocks = await self.repository.fetch_top_stock_from_db(request)

        if not top_stocks:
            raise ResourceNotFoundError("No top stocks found for the given request.")

        recommended_stock = max(
            top_stocks, key=lambda stock: stock.predicted_price_upper_bound
        )

        def calculate_is_increase(stock):
            return stock.predicted_price_upper_bound > stock.predicted_price_lower_bound

        response = TopStockResponseSchema(
            recommended_stock=RecommendedStockSchema(
                name=recommended_stock.stock_name,
                predicted_price_upper_bound=recommended_stock.predicted_price_upper_bound,
                predicted_price_lower_bound=recommended_stock.predicted_price_lower_bound,
                is_increase=calculate_is_increase(recommended_stock),
            ),
            other_stocks=[
                OtherStockSchema(
                    name=stock.stock_name,
                    is_increase=calculate_is_increase(stock),
                )
                for stock in sorted(
                    top_stocks,
                    key=lambda x: x.predicted_price_upper_bound,
                    reverse=True,
                )
                if stock.stock_name != recommended_stock.stock_name
            ],
        )

        return response

    async def calculate_top_stock(
        self, request: TopStockRequestSchema, db: AsyncSession
    ) -> TopStockResponseSchema:
        return await self.get_top_stock(request, db)
