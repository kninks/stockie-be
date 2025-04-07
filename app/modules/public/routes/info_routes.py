from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.response_handlers import (
    BaseSuccessResponse,
    success_response,
)
from app.core.dependencies.db_session import get_db
from app.modules.public.controllers.info_controller import (
    InfoController,
    get_info_controller,
)
from app.modules.public.schema.info_schema import InitialInfoResponseSchema

router = APIRouter(
    prefix="/info",
)


@router.get("", response_model=BaseSuccessResponse[InitialInfoResponseSchema])
async def get_initial_info(
    controller: InfoController = Depends(get_info_controller),
    db: AsyncSession = Depends(get_db),
):
    response: InitialInfoResponseSchema = await controller.initialize_info_controller(
        db=db
    )
    return success_response(data=response)
