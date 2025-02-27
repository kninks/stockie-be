# from datetime import datetime, timedelta
# from sqlalchemy.ext.asyncio import AsyncSession
# from app.repositories.prediction_repository import get_prediction_results
# from app.schemas.prediction_schema import PredictionQuerySchema
#
# async def get_predictions(db: AsyncSession, query_params: PredictionQuerySchema):
    # ✅ Compute the start date using `period`
    # start_date = datetime.utcnow() - timedelta(days=query_params.period)

    # ✅ Update query_params with calculated start_date
    # query_params_dict = query_params.dict()
    # query_params_dict["start_date"] = start_date
    # query_params_dict["end_date"] = datetime.utcnow()

    # ✅ Fetch predictions from repository
    # return await get_prediction_results(db, query_params_dict)