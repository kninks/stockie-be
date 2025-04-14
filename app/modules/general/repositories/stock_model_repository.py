import logging
from typing import List, Optional, Set

from sqlalchemy import delete, select, update
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.exceptions.custom_exceptions import DBError
from app.core.common.utils.validators import sanitize_batch
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Stock, StockModel

logger = logging.getLogger(__name__)


class StockModelRepository:
    ALLOWED_FIELDS: Set[str] = {
        "stock_ticker",
        "version",
        "accuracy",
        "model_path",
        "scaler_path",
        "is_active",
        "features_used",
        "additional_data",
    }

    # TODO: Add pagination
    @staticmethod
    async def fetch_all(db: AsyncSession) -> List[StockModel]:
        stmt = select(StockModel)
        result = await db.execute(stmt)
        stock_models: List[StockModel] = list(result.scalars().all())
        return stock_models

    # TODO: Add pagination
    @staticmethod
    async def fetch_active(
        db: AsyncSession, is_active: Optional[bool] = True
    ) -> List[StockModel]:
        stmt = select(StockModel).where(StockModel.is_active.is_(is_active))
        result = await db.execute(stmt)
        stock_models: List[StockModel] = list(result.scalars().all())
        return stock_models

    @staticmethod
    async def fetch_by_id(db: AsyncSession, stock_model_id: int) -> StockModel:
        stmt = select(StockModel).where(StockModel.id == stock_model_id)
        result = await db.execute(stmt)
        stock_model = result.scalar_one_or_none()
        return stock_model

    @staticmethod
    async def fetch_by_ids(
        db: AsyncSession, stock_model_ids: List[int]
    ) -> List[StockModel]:
        stmt = select(StockModel).where(StockModel.id.in_(stock_model_ids))
        result = await db.execute(stmt)
        stock_models: List[StockModel] = list(result.scalars().all())
        return stock_models

    @staticmethod
    async def fetch_active_by_stock_ticker(
        db: AsyncSession, stock_ticker: str
    ) -> StockModel:
        stmt = select(StockModel).where(
            StockModel.stock_ticker == stock_ticker, StockModel.is_active.is_(True)
        )
        result = await db.execute(stmt)
        stock_model = result.scalar_one_or_none()
        return stock_model

    @staticmethod
    async def fetch_active_by_stock_tickers(
        db: AsyncSession, stock_tickers: List[str]
    ) -> List[StockModel]:
        stmt = select(StockModel).where(
            StockModel.stock_ticker.in_(stock_tickers), StockModel.is_active.is_(True)
        )
        result = await db.execute(stmt)
        stock_models: List[StockModel] = list(result.scalars().all())
        return stock_models

    @staticmethod
    async def fetch_active_by_industry_code(
        db: AsyncSession, industry_code: IndustryCodeEnum
    ) -> list[StockModel]:
        stmt = (
            select(StockModel)
            .join(Stock)
            .where(Stock.industry_code == industry_code, StockModel.is_active.is_(True))
        )
        result = await db.execute(stmt)
        stock_models: List[StockModel] = list(result.scalars().all())
        return stock_models

    @staticmethod
    async def fetch_active_by_industry_codes(
        db: AsyncSession, industry_codes: List[IndustryCodeEnum]
    ) -> list[StockModel]:
        stmt = (
            select(StockModel)
            .join(Stock)
            .where(
                Stock.industry_code.in_(industry_codes), StockModel.is_active.is_(True)
            )
        )
        result = await db.execute(stmt)
        stock_models: List[StockModel] = list(result.scalars().all())
        return stock_models

    @staticmethod
    async def create_one(db: AsyncSession, model_data: dict) -> StockModel:
        sanitized_data = sanitize_batch(
            [model_data], allowed_fields=StockModelRepository.ALLOWED_FIELDS
        )[0]

        try:
            model_object = StockModel(**sanitized_data)
            db.add(model_object)
            await db.flush()
            await db.commit()
            await db.refresh(model_object)
            return model_object
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create stock model: {e}")
            raise DBError("Failed to create stock model") from e

    @staticmethod
    async def create_multiple(
        db: AsyncSession, model_data_list: List[dict]
    ) -> List[StockModel]:
        sanitized_data_list = sanitize_batch(
            model_data_list, allowed_fields=StockModelRepository.ALLOWED_FIELDS
        )

        try:
            model_objects = [StockModel(**data) for data in sanitized_data_list]
            db.add_all(model_objects)
            await db.flush()
            await db.commit()
            for obj in model_objects:
                await db.refresh(obj)
            return model_objects
        except SQLAlchemyError as e:
            await db.rollback()
            logger.error(f"Failed to create multiple stock models: {e}")
            raise DBError("Failed to create stock models") from e

    @staticmethod
    async def update_by_id(
        db: AsyncSession, stock_model_id: int, update_data: dict
    ) -> Optional[StockModel]:
        stock_model = await StockModelRepository.fetch_by_id(db, stock_model_id)
        if stock_model:
            for key, value in update_data.items():
                setattr(stock_model, key, value)
            await db.commit()
            await db.refresh(stock_model)
            return stock_model
        return None

    @staticmethod
    async def update_by_ids(
        db: AsyncSession, stock_model_ids: List[int], update_data: dict
    ) -> int:
        stmt = (
            update(StockModel)
            .where(StockModel.id.in_(stock_model_ids))
            .values(**update_data)
        )
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount

    async def update_by_stock_ticker(
        self, db: AsyncSession, stock_ticker: str, update_data: dict
    ) -> Optional[StockModel]:
        stock_model = await self.fetch_active_by_stock_ticker(db, stock_ticker)
        if stock_model:
            for key, value in update_data.items():
                setattr(stock_model, key, value)
            await db.commit()
            await db.refresh(stock_model)
            return stock_model
        return None

    async def update_by_stock_tickers(
        self, db: AsyncSession, stock_tickers: list[str], update_data: dict
    ) -> int:
        stock_model = await self.fetch_active_by_stock_tickers(db, stock_tickers)
        if stock_model or len(stock_model) != 0:
            stmt = (
                update(StockModel)
                .where(StockModel.id.in_(stock_tickers))
                .values(**update_data)
            )
            result = await db.execute(stmt)
            await db.commit()
            return result.rowcount
        return 0

    async def delete_by_id(self, db: AsyncSession, stock_model_id: int) -> bool:
        stock_model = await self.fetch_by_id(db, stock_model_id)
        if stock_model:
            await db.delete(stock_model)
            await db.commit()
            return True
        return False

    @staticmethod
    async def delete_by_ids(db: AsyncSession, stock_model_ids: List[int]) -> int:
        stmt = delete(StockModel).where(StockModel.id.in_(stock_model_ids))
        result = await db.execute(stmt)
        await db.commit()
        return result.rowcount
