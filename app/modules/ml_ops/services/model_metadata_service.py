import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.validators import (
    normalize_stock_ticker,
    validate_entity_exists,
    validate_required,
)
from app.core.enums.features_enum import FeatureEnum
from app.models import StockModel
from app.modules.general.services.stock_model_service import (
    StockModelService,
    get_stock_model_service,
)
from app.modules.ml_ops.repositories.model_metadata_repository import (
    ModelMetadataRepository,
)
from app.modules.ml_ops.schemas.model_metadata_schema import (
    ModelMetadataResponseSchema,
)

logger = logging.getLogger(__name__)


class ModelMetadataService:
    def __init__(
        self,
        model_metadata_repository: ModelMetadataRepository,
        stock_model_service: StockModelService,
    ):
        self.model_metadata_repo = model_metadata_repository
        self.stock_model_service = stock_model_service

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
                features_used=[FeatureEnum(feature) for feature in model.features_used],
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
        features_used: list[FeatureEnum],
        additional_data: Optional[dict],
        db: AsyncSession,
    ) -> StockModel:
        validate_required(stock_ticker, "Stock ticker")
        validate_required(version, "Version")
        validate_required(accuracy, "Accuracy")
        validate_required(model_path, "Model path")
        validate_required(scaler_path, "Scaler path")
        validate_required(features_used, "Features")
        stock_ticker = normalize_stock_ticker(stock_ticker)

        try:
            features_used_str = [feature.value for feature in features_used]
            model = await self.model_metadata_repo.update_and_create_model_metadata(
                db=db,
                stock_ticker=stock_ticker,
                version=version,
                accuracy=accuracy,
                model_path=model_path,
                scaler_path=scaler_path,
                features_used=features_used_str,
                additional_data=additional_data,
            )
        except Exception as e:
            logger.error(f"Failed to save model metadata: {e}")
            raise e

        validate_entity_exists(model, "Model")
        return model


def get_model_metadata_service() -> ModelMetadataService:
    return ModelMetadataService(
        model_metadata_repository=ModelMetadataRepository(),
        stock_model_service=get_stock_model_service(),
    )
