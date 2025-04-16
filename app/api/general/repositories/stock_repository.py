from typing import Optional

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
        db: AsyncSession, stock_tickers: list[str]
    ) -> list[Stock]:
        stmt = (
            select(Stock).where(Stock.ticker.in_(stock_tickers)).order_by(Stock.ticker)
        )
        result = await db.execute(stmt)
        stocks: list[Stock] = list(result.scalars().all())
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
        stocks: list[Stock] = list(result.scalars().all())
        return stocks

    @staticmethod
    async def fetch_by_industry_codes(
        db: AsyncSession,
        industry_codes: list[IndustryCodeEnum],
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
        stocks: list[Stock] = list(result.scalars().all())
        return stocks

    @staticmethod
    async def create_stock(
        db: AsyncSession,
        stock_ticker: str,
        industry_code: IndustryCodeEnum,
        stock_name: str,
        stock_description: Optional[str] = None,
    ) -> Stock:
        stock = Stock(
            ticker=stock_ticker,
            name=stock_name,
            description=stock_description,
            industry_code=industry_code,
        )
        db.add(stock)
        await db.commit()
        await db.refresh(stock)
        return stock

    async def update_by_ticker(
        self,
        db: AsyncSession,
        stock_ticker: str,
        industry_code: Optional[IndustryCodeEnum],
        stock_name: Optional[str],
        is_active: Optional[bool],
        stock_description: Optional[str] = None,
    ) -> Optional[Stock]:
        stock = await self.fetch_by_ticker(db=db, stock_ticker=stock_ticker)

        if stock:
            if industry_code:
                stock.industry_code = industry_code
            if stock_name:
                stock.name = stock_name
            if is_active is not None:
                stock.is_active = is_active
            if stock_description:
                stock.description = stock_description
            await db.commit()
            await db.refresh(stock)
            return stock
        return None
