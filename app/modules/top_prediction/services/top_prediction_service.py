from datetime import date

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import ResourceNotFoundError
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Prediction
from app.modules.top_prediction.repositories.industry_repository import (
    IndustryRepository,
)
from app.modules.top_prediction.repositories.prediction_repository import (
    PredictionRepository,
)
from app.modules.top_prediction.repositories.top_prediction_repository import (
    TopPredictionRepository,
)
from app.modules.top_prediction.schema.top_prediction_api_schema import (
    TopPredictionRequestSchema,
    TopPredictionResponseSchema,
)
from app.modules.top_prediction.services.types.ranked_prediction import RankedPrediction


class TopPredictionService:

    def __init__(self):
        self.industry_repo = IndustryRepository()
        self.prediction_repo = PredictionRepository()
        self.top_prediction_repo = TopPredictionRepository()

    async def get_top_prediction(
        self, request: TopPredictionRequestSchema, db: AsyncSession
    ) -> TopPredictionResponseSchema:
        industry_id = await self.get_industry_id_by_code(db, request.industry)

        # target_date = date.today()
        target_date = date(2025, 3, 28)  # temporary

        top_prediction = await self.top_prediction_repo.fetch_top_prediction_from_db(
            db=db,
            industry_id=industry_id,
            period=request.period,
            target_date=target_date,
        )

        if not top_prediction:
            raise ResourceNotFoundError("No top prediction found.")

        # add is increasing?
        return TopPredictionResponseSchema(ranked_stocks=top_prediction)

    async def calculate_and_save_top_prediction(
        self, request: TopPredictionRequestSchema, db: AsyncSession
    ):
        industry_id = await self.get_industry_id_by_code(db, request.industry)

        # target_date = date.today()
        target_date = date(2025, 3, 28)  # temporary
        predictions = await self.prediction_repo.fetch_ranked_predictions(
            db=db,
            industry_id=industry_id,
            period=request.period,
            target_date=target_date,
        )

        if len(predictions) != 5:
            raise ResourceNotFoundError("Incorrect number of predictions.")

        ranked_predictions = self.rank_prediction(predictions)

        await self.top_prediction_repo.save_top_prediction(
            db=db,
            industry_id=industry_id,
            period=request.period,
            target_date=target_date,
            ranked_predictions=ranked_predictions,
        )

    async def get_industry_id_by_code(
        self, db: AsyncSession, code: IndustryCodeEnum
    ) -> int:
        industry = await self.industry_repo.get_by_code(db=db, code=code)
        return industry.id

    @staticmethod
    def rank_prediction(predictions: list[Prediction]) -> list[RankedPrediction]:
        predictions.sort(key=lambda x: x.predicted_price / x.actual_price, reverse=True)
        ranked_predictions = [
            RankedPrediction(prediction=p, rank=i + 1)
            for i, p in enumerate(predictions[:5])
        ]
        return ranked_predictions
