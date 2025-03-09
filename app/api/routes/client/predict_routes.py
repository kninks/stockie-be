from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.controllers.client.predict_controller import PredictController
from app.common.dependencies.api_key_auth import verify_role
from app.common.dependencies.get_db import get_db

from app.schemas.client.predict.predict_request_schema import PredictRequestSchema
from app.common.utils.response_handler import success_response

router = APIRouter()


@router.post("/get-predict")
async def get_prediction(
    request: PredictRequestSchema,
    db: AsyncSession = Depends(get_db),
    user_role: str = Depends(verify_role(["client"])),
):
    """
    1. fetch from db
    2. calculate the recommended stock with the highest predicted price?
    3. return the stock name and predicted price
    4. sort the rest of the stocks by predicted price
    5. for each of the rest, return the stock name and increase or decrease
    """
    return await success_response(data=await PredictController.predict(request, db))
