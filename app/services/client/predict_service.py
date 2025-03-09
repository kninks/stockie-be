from sqlalchemy.ext.asyncio import AsyncSession

from app.common.exceptions.custom_exceptions import ResourceNotFoundError
from app.repositories.client.predict_repository import PredictRepository
from app.schemas.client.predict.predict_request_schema import PredictRequestSchema
from app.schemas.client.predict.predict_response_schema import (
    PredictResponseSchema,
    RecommendedStockSchema,
    OtherStockSchema,
)


class PredictService:

    def __init__(self):
        self.repository = PredictRepository()

    async def get_predictions(
        self, request: PredictRequestSchema, db: AsyncSession
    ) -> PredictResponseSchema:
        stock_predictions = await self.repository.fetch_predictions(request)

        if not stock_predictions:
            raise ResourceNotFoundError("No predictions found for the given request.")

        recommended_stock = max(
            stock_predictions, key=lambda stock: stock.predicted_price_upper_bound
        )

        def calculate_is_increase(stock):
            return stock.predicted_price_upper_bound > stock.predicted_price_lower_bound

        response = PredictResponseSchema(
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
                    stock_predictions,
                    key=lambda x: x.predicted_price_upper_bound,
                    reverse=True,
                )
                if stock.stock_name != recommended_stock.stock_name
            ],
        )

        return response
