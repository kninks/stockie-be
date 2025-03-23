from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.api_key_auth import verify_role
from app.core.dependencies.get_db import get_db
from app.core.enums.industry_enum import IndustryEnum
from app.core.enums.period_enum import PeriodEnum
from app.core.enums.roles_enum import RoleEnum
from app.modules.top_stock.controllers.top_stock_controller import TopStockController
from app.modules.top_stock.schema.top_stock_api_schema import (
    TopStockRequestSchema,
    TopStockResponseSchema,
)

router = APIRouter(
    prefix="/top-stock",
    tags=["Top Stock"],
)


@router.post("/top-stock")
async def route_get_top_stock(
    request: TopStockRequestSchema,
    db: AsyncSession = Depends(get_db),
    user_role: str = Depends(verify_role([RoleEnum.CLIENT.value])),
):
    """
    1. fetch from db
    2. calculate the recommended stock with the highest predicted price?
    3. return the stock name and predicted price
    4. sort the rest of the stocks by predicted price
    5. for each of the rest, return the stock name and increase or decrease
    """
    return await success_response(
        data=await TopStockController.get_top_stock_response(request, db)
    )


@router.get("")
async def route_get_top_stock2(
    industry: IndustryEnum = Query(...),
    period: PeriodEnum = Query(...),
    db: AsyncSession = Depends(get_db),
    user_role: str = Depends(verify_role([RoleEnum.CLIENT.value])),
):
    """
    fetch the calculated result from db
    """
    request: TopStockRequestSchema = TopStockRequestSchema(
        industry=industry, period=period
    )
    response: TopStockResponseSchema = await TopStockController.get_top_stock_response(
        request, db
    )
    return await success_response(data=response)


@router.post("/calculate")
async def route_calculate_top_stock(
    request: TopStockRequestSchema,
    db: AsyncSession = Depends(get_db),
):
    """
    1. fetch from db
    2. calculate the recommended stock with the highest predicted price?
    3. return the stock name and predicted price
    4. sort the rest of the stocks by predicted price
    5. for each of the rest, return the stock name and increase or decrease
    """
    response: TopStockResponseSchema = await TopStockController.get_top_stock_response(
        request, db
    )
    return await success_response(data=response)
