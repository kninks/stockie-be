import logging
from typing import Optional

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
from app.core.enums.industry_code_enum import IndustryCodeEnum
from app.models import Stock
from app.modules.general.repositories.stock_repository import StockRepository

logger = logging.getLogger(__name__)


class StockService:
    def __init__(self, stock_repository: StockRepository):
        self.stock_repo = stock_repository

    async def get_all(self, db: AsyncSession) -> list[Stock]:
        try:
            stocks = await self.stock_repo.fetch_all(db=db)
        except Exception as e:
            logger.error(f"Failed to fetch all stocks: {e}")
            raise DBError("Failed to fetch all stocks") from e

        validate_entity_exists(stocks, "Stocks")
        return stocks

    async def get_active(
        self, db: AsyncSession, is_active: Optional[bool] = True
    ) -> list[Stock]:
        try:
            stocks = await self.stock_repo.fetch_active(db=db, is_active=is_active)
        except Exception as e:
            logger.error(f"Failed to fetch active stocks: {e}")
            raise DBError("Failed to fetch active stocks") from e

        validate_entity_exists(stocks, "Active stocks")
        if is_active:
            validate_exact_length(stocks, 40, "active stocks")
        return stocks

    async def get_active_ticker_values(
        self, db: AsyncSession, is_active: Optional[bool] = True
    ) -> list[str]:
        try:
            stocks = await self.stock_repo.fetch_active_ticker_values(
                db=db, is_active=is_active
            )
        except Exception as e:
            logger.error(f"Failed to fetch active stock ticker values: {e}")
            raise DBError("Failed to fetch active stock ticker values") from e

        validate_entity_exists(stocks, "Active stock ticker values")
        if is_active:
            validate_exact_length(stocks, 40, "active stock ticker values")
        return stocks

    async def get_by_ticker(self, db: AsyncSession, stock_ticker: str) -> Stock:
        validate_required(stock_ticker, "stock ticker")
        stock_ticker = normalize_stock_ticker(stock_ticker)

        try:
            stock = await self.stock_repo.fetch_by_ticker(
                db=db, stock_ticker=stock_ticker
            )
        except Exception as e:
            logger.error(f"Failed to fetch stock with ticker '{stock_ticker}': {e}")
            raise DBError("Failed to fetch stock") from e

        validate_entity_exists(stock, f"Stock ticker '{stock_ticker}'")
        return stock

    async def get_by_tickers(
        self, db: AsyncSession, stock_tickers: list[str]
    ) -> list[Stock]:
        validate_required(stock_tickers, "stock tickers")
        stock_tickers = normalize_stock_tickers(stock_tickers)

        try:
            if len(stock_tickers) == 1:
                stock = await self.stock_repo.fetch_by_ticker(
                    db=db, stock_ticker=stock_tickers[0]
                )
                stocks = [stock] if stock else []
            else:
                stocks = await self.stock_repo.fetch_by_tickers(
                    db=db, stock_tickers=stock_tickers
                )
        except Exception as e:
            logger.error(f"Failed to fetch stocks for tickers {stock_tickers}: {e}")
            raise DBError("Failed to fetch stocks") from e

        validate_entity_exists(stocks, f"Stocks for tickers {stock_tickers}")
        validate_exact_length(stocks, len(stock_tickers), "stocks")
        return stocks

    async def get_by_industry_code(
        self,
        db: AsyncSession,
        industry_code: IndustryCodeEnum,
        is_active: Optional[bool] = True,
    ) -> list[Stock]:
        validate_required(industry_code, "industry code")
        validate_enum_input(industry_code, IndustryCodeEnum, "industry code")

        try:
            stocks = await self.stock_repo.fetch_by_industry_code(
                db=db, industry_code=industry_code, is_active=is_active
            )
        except Exception as e:
            logger.error(f"Failed to fetch stocks for industry '{industry_code}': {e}")
            raise DBError("Failed to fetch stocks") from e

        validate_entity_exists(stocks, f"Stocks in industry '{industry_code}'")
        if is_active:
            validate_exact_length(stocks, 5, f"stocks in industry '{industry_code}'")
        return stocks

    async def get_by_industry_codes(
        self,
        db: AsyncSession,
        industry_codes: list[IndustryCodeEnum],
        is_active: Optional[bool] = True,
    ) -> list[Stock]:
        validate_required(industry_codes, "industry codes")
        validate_enum_input(industry_codes, IndustryCodeEnum, "industry codes")

        try:
            if len(industry_codes) == 1:
                stocks = await self.stock_repo.fetch_by_industry_code(
                    db=db, industry_code=industry_codes[0], is_active=is_active
                )
            else:
                stocks = await self.stock_repo.fetch_by_industry_codes(
                    db=db, industry_codes=industry_codes, is_active=is_active
                )
        except Exception as e:
            logger.error(f"Failed to fetch stocks for industries {industry_codes}: {e}")
            raise DBError("Failed to fetch stocks") from e

        validate_entity_exists(stocks, f"Stocks for industries {industry_codes}")
        if is_active:
            validate_exact_length(
                stocks, 5 * len(industry_codes), "stocks by industry codes"
            )
        return stocks

    async def create_stock(
        self,
        db: AsyncSession,
        stock_ticker: str,
        industry_code: IndustryCodeEnum,
        stock_name: str,
        stock_description: Optional[str] = None,
    ) -> Stock:
        validate_required(stock_ticker, "stock ticker")
        validate_required(industry_code, "industry code")
        validate_required(stock_name, "stock name")
        normalized_stock_ticker = normalize_stock_ticker(stock_ticker)

        try:
            stock = await self.stock_repo.create_stock(
                db=db,
                stock_ticker=normalized_stock_ticker,
                industry_code=industry_code,
                stock_name=stock_name,
                stock_description=stock_description,
            )
        except Exception as e:
            logger.error(f"Failed to create stock '{stock_ticker}': {e}")
            raise DBError("Failed to create stock") from e

        validate_entity_exists(stock, f"Stock '{stock_ticker}'")
        return stock


def get_stock_service() -> StockService:
    return StockService(stock_repository=StockRepository())
