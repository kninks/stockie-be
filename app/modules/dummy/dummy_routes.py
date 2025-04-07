import random
from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, Query
from fastapi.encoders import jsonable_encoder
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.response_handlers import success_response
from app.core.dependencies.api_key_auth import verify_role
from app.core.dependencies.db_session import get_db
from app.models import ClosingPrice
from app.modules.dummy.dummy_controller import DummyController, get_dummy_controller

router = APIRouter(
    prefix="/dummy",
    tags=["Dummy"],
    dependencies=[Depends(verify_role([]))],
)


@router.post("/closing-prices")
async def dummy_closing_prices(db: AsyncSession = Depends(get_db)):
    tickers = [
        'AGRO1',
        'AGRO2',
        'AGRO3',
        'AGRO4',
        'AGRO5',
        'CONS1',
        'CONS2',
        'CONS3',
        'CONS4',
        'CONS5',
        'FIN1',
        'FIN2',
        'FIN3',
        'FIN4',
        'FIN5',
        'IND1',
        'IND2',
        'IND3',
        'IND4',
        'IND5',
        'PROP1',
        'PROP2',
        'PROP3',
        'PROP4',
        'PROP5',
        'RES1',
        'RES2',
        'RES3',
        'RES4',
        'RES5',
        'SERV1',
        'SERV2',
        'SERV3',
        'SERV4',
        'SERV5',
        'TECH1',
        'TECH2',
        'TECH3',
        'TECH4',
        'TECH5',
    ]
    end_date = datetime.strptime('2025-04-01', '%Y-%m-%d')
    num_days = 90
    data_to_insert = []
    for ticker in tickers:
        price = random.uniform(120, 200)
        for i in range(num_days):
            date = end_date - timedelta(days=num_days - i - 1)
            price += random.uniform(-5, 5)
            price = round(max(price, 80), 2)
            data_to_insert.append(
                ClosingPrice(
                    stock_ticker=ticker, target_date=date.date(), closing_price=price
                )
            )
    db.add_all(data_to_insert)
    await db.commit()
    serialized_data = jsonable_encoder(data_to_insert)
    return success_response(data=serialized_data)


@router.post("/inference-results/all")
async def dummy_inference_results_all(
    db: AsyncSession = Depends(get_db),
    controller: DummyController = Depends(get_dummy_controller),
    stock_tickers: list[str] = Query(...),
    target_date: date = Query(...),
    days_back: int = Query(...),
    days_forward: int = Query(...),
):
    response = await controller.generate_dummy_inference_results_all_controller(
        db=db,
        target_date=target_date,
        days_back=days_back,
        days_forward=days_forward,
    )
    return success_response(response)


@router.get("/inference-results")
async def dummy_inference_results(
    db: AsyncSession = Depends(get_db),
    controller: DummyController = Depends(get_dummy_controller),
    stock_tickers: list[str] = Query(...),
    target_date: date = Query(...),
    days_back: int = Query(...),
    days_forward: int = Query(...),
):
    response = await controller.generate_dummy_inference_results_controller(
        db=db,
        stock_tickers=stock_tickers,
        target_date=target_date,
        days_back=days_back,
        days_forward=days_forward,
    )
    return success_response(response)
