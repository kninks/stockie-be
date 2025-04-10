from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.common.utils.response_handlers import (
    success_response,
)
from app.core.dependencies.api_key_auth import verify_role
from app.core.dependencies.db_session import get_db
from app.modules.internal.controllers.internal_controller import (
    InternalController,
    get_internal_controller,
)
from app.modules.internal.routes import cleanup_data_routes, job_config_routes
from app.modules.internal.schemas.internal_schema import (
    PullFeaturesRequestSchema,
    RankPredictionsRequestSchema,
)

router = APIRouter(
    prefix="/internal",
    tags=["Internal"],
    dependencies=[Depends(verify_role([]))],
)


@router.post("/rank-predictions")
async def rank_predictions_route(
    request: RankPredictionsRequestSchema,
    controller: InternalController = Depends(get_internal_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.rank_predictions_controller(request=request, db=db)
    return success_response()


@router.post("/pull-features")
async def pull_features_route(
    request: PullFeaturesRequestSchema,
    controller: InternalController = Depends(get_internal_controller),
    db: AsyncSession = Depends(get_db),
):
    await controller.pull_features_controller(request=request, db=db)
    return success_response()


router.include_router(cleanup_data_routes.router)
router.include_router(job_config_routes.router)
