import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.api.general.services.stock_model_service import (
    StockModelService,
    get_stock_model_service,
)
from app.api.general.services.stock_service import StockService, get_stock_service
from app.api.ml_ops.repositories.metadata_repository import (
    MetadataRepository,
)
from app.api.ml_ops.schemas.metadata_schema import (
    ModelMetadataResponseSchema,
)
from app.core.common.utils.validators import (
    normalize_stock_ticker,
    validate_entity_exists,
    validate_required,
)
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.core.enums.trading_data_enum import TradingDataEnum
from app.models import Stock, StockModel

logger = logging.getLogger(__name__)


class MetadataService:
    def __init__(
        self,
        metadata_repository: MetadataRepository,
        stock_model_service: StockModelService,
        stock_service: StockService,
    ):
        self.metadata_repo = metadata_repository
        self.stock_model_service = stock_model_service
        self.stock_service = stock_service

    async def insert_stock(
        self,
        db: AsyncSession,
        stock_ticker: str,
        industry_code: IndustryCodeEnum,
        stock_name: str,
        stock_description: Optional[str],
    ) -> Optional[Stock]:
        try:
            stock = await self.stock_service.create_stock(
                db=db,
                stock_ticker=stock_ticker,
                industry_code=industry_code,
                stock_name=stock_name,
                stock_description=stock_description,
            )
            if not stock:
                logger.error(f"Failed to create stock: {stock_ticker}")
                return None

            return stock
        except Exception as e:
            logger.error(f"Failed to insert stock: {e}")
            raise e

    async def update_stock(
        self,
        db: AsyncSession,
        stock_ticker: str,
        industry_code: Optional[IndustryCodeEnum] = None,
        stock_name: Optional[str] = None,
        is_active: Optional[bool] = None,
        stock_description: Optional[str] = None,
    ) -> Optional[Stock]:
        validate_required(stock_ticker, "stock ticker")
        stock_ticker = normalize_stock_ticker(stock_ticker)

        try:
            stock = await self.stock_service.update_by_ticker(
                db=db,
                stock_ticker=stock_ticker,
                industry_code=industry_code,
                stock_name=stock_name,
                is_active=is_active,
                stock_description=stock_description,
            )
            if not stock:
                logger.error(f"Failed to update stock: {stock_ticker}")
                return None

        except Exception as e:
            logger.error(f"Failed to update stock: {e}")
            raise e
        validate_entity_exists(stock, f"Stock '{stock_ticker}'")
        return stock

    # DONE
    async def get_stock_model(
        self, stock_tickers: list[str], db: AsyncSession
    ) -> list[ModelMetadataResponseSchema]:
        models = await self.stock_model_service.get_active_by_stock_tickers(
            db=db, stock_tickers=stock_tickers
        )

        return [
            ModelMetadataResponseSchema(
                model_id=model.id,
                stock_ticker=model.stock_ticker,
                version=model.version,
                accuracy=model.accuracy,
                model_path=model.model_path,
                scaler_path=model.scaler_path,
                features_used=[
                    TradingDataEnum(feature) for feature in model.features_used
                ],
                additional_data=model.additional_data,
            )
            for model in models
        ]

    # TODO: check if correct
    async def save_stock_model(
        self,
        stock_ticker: str,
        version: str,
        accuracy: float,
        model_path: str,
        scaler_path: str,
        features_used: list[TradingDataEnum],
        additional_data: Optional[dict],
        db: AsyncSession,
    ) -> StockModel:
        validate_required(stock_ticker, "Stock ticker")
        validate_required(version, "Version")
        validate_required(accuracy, "Accuracy")
        validate_required(model_path, "Model path")
        validate_required(scaler_path, "Scaler path")
        validate_required(features_used, "Features used")
        stock_ticker = normalize_stock_ticker(stock_ticker)

        try:
            model = await self.metadata_repo.update_and_create_model_metadata(
                db=db,
                stock_ticker=stock_ticker,
                version=version,
                accuracy=accuracy,
                model_path=model_path,
                scaler_path=scaler_path,
                features_used=features_used,
                additional_data=additional_data,
            )
        except Exception as e:
            logger.error(f"Failed to save model metadata: {e}")
            raise e

        validate_entity_exists(model, "Model")
        return model


def get_metadata_service() -> MetadataService:
    return MetadataService(
        metadata_repository=MetadataRepository(),
        stock_model_service=get_stock_model_service(),
        stock_service=get_stock_service(),
    )
