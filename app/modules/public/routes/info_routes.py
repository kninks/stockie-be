from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.response_handlers import (
    BaseSuccessResponse,
    success_response,
)
from app.core.dependencies.api_key_auth import verify_role
from app.core.dependencies.db_session import get_db
from app.core.enums.roles_enum import RoleEnum
from app.modules.public.controllers.info_controller import InfoController
from app.modules.public.schema.info_schema import IndustryResponseSchema

router = APIRouter(
    prefix="/info",
    tags=["Information"],
    dependencies=[Depends(verify_role([RoleEnum.CLIENT.value]))],
)


@router.get("", response_model=BaseSuccessResponse[list[IndustryResponseSchema]])
async def get_initial_info(
    controller: InfoController = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Initialized all info
    """
    response: list[IndustryResponseSchema] = (
        await controller.initialize_info_controller(db=db)
    )
    return success_response(data=response)


@router.get(
    "/industry", response_model=BaseSuccessResponse[list[IndustryResponseSchema]]
)
async def get_all_industries_routes(
    controller: InfoController = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Get the list of industries
    """
    response: list[IndustryResponseSchema] = (
        await controller.get_all_industries_controller(db=db)
    )
    return success_response(data=response)


# @router.get("/{industry_code}/stocks")
# async def get_stocks_by_industry(
#         industry_code: IndustryCodeEnum,
#         controller: InfoController = Depends(),
#         db: AsyncSession = Depends(get_db),
# ):
#     """
#     Get the list of stocks for a specific industry
#     """
#     response = await controller.get_stocks_by_industry_controller(industry_code=industry_code, db=db)
#     return await success_response(data=response)
