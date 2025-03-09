from typing import List, Any

from app.schemas.client.predict.predict_repo_schema import PredictRepoSchema
from app.schemas.client.predict.predict_request_schema import PredictRequestSchema


class PredictRepository:
    """Handles database operations related to stock predictions."""

    async def fetch_predictions(
        self, request: PredictRequestSchema
    ) -> List[PredictRepoSchema]:
        """Dummy function to simulate fetching stock predictions from the database."""
        dummy_data = [
            {
                "stock_name": "AAPL",
                "predicted_price_upper_bound": 185.50,
                "predicted_price_lower_bound": 180.00,
            },
            {
                "stock_name": "TSLA",
                "predicted_price_upper_bound": 250.00,
                "predicted_price_lower_bound": 245.50,
            },
            {
                "stock_name": "GOOGL",
                "predicted_price_upper_bound": 2950.00,
                "predicted_price_lower_bound": 2920.00,
            },
            {
                "stock_name": "MSFT",
                "predicted_price_upper_bound": 320.00,
                "predicted_price_lower_bound": 315.00,
            },
            {
                "stock_name": "AMZN",
                "predicted_price_upper_bound": 3450.00,
                "predicted_price_lower_bound": 3400.00,
            },
        ]

        return [PredictRepoSchema(**stock) for stock in dummy_data]
