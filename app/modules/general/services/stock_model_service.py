import logging
from typing import List

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import (
    normalize_stock_ticker,
    normalize_stock_tickers,
    validate_entity_exists,
    validate_enum_input,
    validate_exact_length,
    validate_required,
)
from app.core.enums.features_enum import validate_features
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import StockModel
from app.modules.general.repositories.stock_model_repository import StockModelRepository

logger = logging.getLogger(__name__)


class StockModelService:
    def __init__(
        self,
        stock_model_repository: StockModelRepository,
    ):
        self.stock_model_repo = stock_model_repository

    async def get_active(self, db: AsyncSession) -> List[StockModel]:
        try:
            stock_models = await self.stock_model_repo.fetch_active(db=db)
        except Exception as e:
            logger.error(f"Failed to fetch active stock models: {e}")
            raise DBError("Failed to fetch active stock models") from e

        validate_entity_exists(stock_models, "Active stock models")
        return stock_models

    async def get_by_id(self, db: AsyncSession, stock_model_id: int) -> StockModel:
        validate_required(stock_model_id, "stock model id")

        try:
            stock_model = await self.stock_model_repo.fetch_by_id(
                db=db, stock_model_id=stock_model_id
            )
        except Exception as e:
            logger.error(f"Failed to fetch stock model '{stock_model_id}': {e}")
            raise DBError("Failed to fetch stock model") from e

        validate_entity_exists(stock_model, f"Stock model {stock_model}")
        return stock_model

    async def get_by_ids(
        self, db: AsyncSession, stock_model_ids: list[int]
    ) -> List[StockModel]:
        validate_required(stock_model_ids, "stock model ids")

        try:
            if len(stock_model_ids) == 1:
                stock_model = await self.stock_model_repo.fetch_by_id(
                    db=db, stock_model_id=stock_model_ids[0]
                )
                stock_models = [stock_model] if stock_model else []
            else:
                stock_models = await self.stock_model_repo.fetch_by_ids(
                    db=db, stock_model_ids=stock_model_ids
                )
        except Exception as e:
            logger.error(f"Failed to fetch stock models: {e}")
            raise DBError("Failed to fetch stock models") from e

        validate_entity_exists(stock_models, "Stock models")
        validate_exact_length(stock_models, len(stock_model_ids), "stock models")
        return stock_models

    async def get_active_by_stock_ticker(
        self, db: AsyncSession, stock_ticker: str
    ) -> StockModel:
        validate_required(stock_ticker, "stock ticker")
        stock_ticker = normalize_stock_ticker(stock_ticker)

        try:
            stock_model = await self.stock_model_repo.fetch_active_by_stock_ticker(
                db=db, stock_ticker=stock_ticker
            )
        except Exception as e:
            logger.error(
                f"Failed to fetch active stock model for '{stock_ticker}': {e}"
            )
            raise DBError("Failed to fetch active stock model") from e

        validate_entity_exists(stock_model, f"Active stock model for {stock_ticker}")
        return stock_model

    async def get_active_by_stock_tickers(
        self, db: AsyncSession, stock_tickers: list[str]
    ) -> list[StockModel]:
        validate_required(stock_tickers, "stock tickers")
        stock_tickers = normalize_stock_tickers(stock_tickers)

        try:
            if len(stock_tickers) == 1:
                stock_model = await self.stock_model_repo.fetch_active_by_stock_ticker(
                    db=db, stock_ticker=stock_tickers[0]
                )
                stock_models = [stock_model] if stock_model else []
            else:
                stock_models = (
                    await self.stock_model_repo.fetch_active_by_stock_tickers(
                        db=db, stock_tickers=stock_tickers
                    )
                )
        except Exception as e:
            logger.error(f"Failed to fetch active stock models: {e}")
            raise DBError("Failed to fetch active stock models") from e

        validate_entity_exists(stock_models, "Active stock models")
        validate_exact_length(stock_models, len(stock_tickers), "active stock models")

        # for model in stock_models:
        #     if model.features_used:
        #         model.features_used = [
        #             FeatureEnum(feature) for feature in model.features_used
        #         ]

        return stock_models

    async def get_active_by_industry_code(
        self, db: AsyncSession, industry_code: IndustryCodeEnum
    ) -> List[StockModel]:
        validate_required(industry_code, "industry code")
        validate_enum_input(industry_code, IndustryCodeEnum, "industry code")

        try:
            stock_models = await self.stock_model_repo.fetch_active_by_industry_code(
                db=db, industry_code=industry_code
            )
        except Exception as e:
            logger.error(
                f"Failed to fetch active stock models for '{industry_code}': {e}"
            )
            raise DBError("Failed to fetch active stock models") from e

        validate_entity_exists(stock_models, f"Active stock models for {industry_code}")
        return stock_models

    async def get_active_by_industry_codes(
        self, db: AsyncSession, industry_codes: List[IndustryCodeEnum]
    ) -> List[StockModel]:
        validate_required(industry_codes, "industry codes")
        validate_enum_input(industry_codes, IndustryCodeEnum, "industry codes")

        try:
            if len(industry_codes) == 1:
                stock_models = (
                    await self.stock_model_repo.fetch_active_by_industry_code(
                        db=db, industry_code=industry_codes[0]
                    )
                )
                stock_models = [stock_models] if stock_models else []
            else:
                stock_models = (
                    await self.stock_model_repo.fetch_active_by_industry_codes(
                        db=db, industry_codes=industry_codes
                    )
                )
        except Exception as e:
            logger.error(f"Failed to fetch active stock models: {e}")
            raise DBError("Failed to fetch active stock models") from e

        validate_entity_exists(stock_models, "Active stock models")
        validate_exact_length(stock_models, len(industry_codes), "active stock models")
        return stock_models

    async def create_one(self, db: AsyncSession, model_data: dict) -> StockModel:
        validate_required(model_data, "stock model data")
        try:
            model_data["stock_ticker"] = normalize_stock_ticker(
                model_data["stock_ticker"]
            )
            features_used = validate_features(model_data.get("features_used", []))
            if features_used:
                model_data["features_used"] = [
                    feature.value for feature in features_used
                ]

            return await self.stock_model_repo.create_one(db=db, model_data=model_data)
        except DBError:
            raise  # Already wrapped
        except SQLAlchemyError as e:
            logger.error(f"Unexpected DB error during create_one: {e}")
            raise DBError("Unexpected error while creating stock model") from e

    # async def create_multiple(
    #     self, db: AsyncSession, model_data_list: list[dict]
    # ) -> List[StockModel]:
    #     validate_required(model_data_list, "stock model data list")
    #
    #     try:
    #         model_data_list = normalize_stock_tickers_in_data(model_data_list)
    #         normalize_stock_tickers(model_data_list)
    #         return await self.stock_model_repo.create_multiple(
    #             db=db, model_data_list=model_data_list
    #         )
    #     except DBError:
    #         raise
    #     except SQLAlchemyError as e:
    #         logger.error(f"Unexpected DB error during create_multiple: {e}")
    #         raise DBError("Unexpected error while creating stock models") from e

    # TODO
    async def deactivate(
        self,
        db: AsyncSession,
        stock_ticker: int,
    ) -> None:
        pass
        # validate_required(stock_ticker, "Stock ticker")
        #
        # try:
        #     updated_count = await self.stock_model_repo.update_by_id(
        #         db=db,
        #         prediction_id=prediction_id,
        #         rank=rank,
        #         top_prediction_id=top_prediction_id,
        #     )
        # except Exception as e:
        #     logger.error(f"Failed to update prediction ID {prediction_id}: {e}")
        #     raise DBError("Failed to update prediction") from e
        #
        # if updated_count == 0:
        #     logger.warning(f"No prediction updated for ID {prediction_id}")
        #     raise ResourceNotFoundError(f"Prediction {prediction_id} not found")

    # TODO
    async def update_batch_rank_and_top_prediction(
        self, db: AsyncSession, updates: List[dict]
    ) -> int:
        """
        updates with a list of {id, rank, top_prediction_id}
        """
        pass
        # validate_required(updates, "prediction updates")
        # for item in updates:
        #     validate_required(item.get("id"), "prediction ID")
        #
        # try:
        #     if len(updates) == 1:
        #         prediction = await self.prediction_repo.update_rank_and_top_id(
        #             db=db,
        #             prediction_id=updates[0]["id"],
        #             rank=updates[0]["rank"],
        #             top_prediction_id=updates[0]["top_prediction_id"],
        #         )
        #         updated_count = 1 if prediction else 0
        #     else:
        #         updated_count = (
        #             await self.prediction_repo.update_batch_rank_and_top_prediction(
        #                 db=db,
        #                 updates=updates,
        #             )
        #         )
        # except Exception as e:
        #     logger.error(
        #         f"Failed to update prediction ranks and top prediction links: {e}"
        #     )
        #     raise DBError("Failed to update predictions") from e
        #
        # logger.info(f"Updated {updated_count} predictions.")
        # return updated_count


def get_stock_model_service() -> StockModelService:
    return StockModelService(stock_model_repository=StockModelRepository())
