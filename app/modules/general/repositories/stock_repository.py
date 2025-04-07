from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import (
    Stock,
)


class StockRepository:
    @staticmethod
    async def fetch_all(db: AsyncSession) -> list[Stock]:
        stmt = select(Stock).order_by(Stock.ticker)
        result = await db.execute(stmt)
        stocks: list[Stock] = list(result.scalars().all())
        return stocks

    @staticmethod
    async def fetch_active(
        db: AsyncSession, is_active: Optional[bool] = True
    ) -> list[Stock]:
        stmt = (
            select(Stock).where(Stock.is_active.is_(is_active)).order_by(Stock.ticker)
        )
        result = await db.execute(stmt)
        stocks: list[Stock] = list(result.scalars().all())
        return stocks

    @staticmethod
    async def fetch_active_ticker_values(
        db: AsyncSession, is_active: Optional[bool] = True
    ) -> list[str]:
        stmt = (
            select(Stock.ticker)
            .where(Stock.is_active.is_(is_active))
            .order_by(Stock.ticker)
        )
        result = await db.execute(stmt)
        stocks: list[str] = list(result.scalars().all())
        return stocks

    @staticmethod
    async def fetch_by_ticker(db: AsyncSession, stock_ticker: str) -> Stock:
        stmt = select(Stock).where(Stock.ticker == stock_ticker).order_by(Stock.ticker)
        result = await db.execute(stmt)
        stock = result.scalar_one_or_none()
        return stock

    @staticmethod
    async def fetch_by_tickers(
        db: AsyncSession, stock_tickers: List[str]
    ) -> List[Stock]:
        stmt = (
            select(Stock).where(Stock.ticker.in_(stock_tickers)).order_by(Stock.ticker)
        )
        result = await db.execute(stmt)
        stocks: List[Stock] = list(result.scalars().all())
        return stocks

    @staticmethod
    async def fetch_by_industry_code(
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        is_active: Optional[bool] = True,
    ) -> list[Stock]:
        stmt = (
            select(Stock)
            .where(Stock.industry_code == industry_code, Stock.is_active.is_(is_active))
            .order_by(Stock.ticker)
        )

        result = await db.execute(stmt)
        stocks: List[Stock] = list(result.scalars().all())
        return stocks

    @staticmethod
    async def fetch_by_industry_codes(
        db: AsyncSession,
        industry_codes: List[IndustryCodeEnum],
        is_active: Optional[bool] = True,
    ) -> list[Stock]:
        stmt = (
            select(Stock)
            .where(
                Stock.industry_code.in_(industry_codes), Stock.is_active.is_(is_active)
            )
            .order_by(Stock.ticker)
        )
        result = await db.execute(stmt)
        stocks: List[Stock] = list(result.scalars().all())
        return stocks
