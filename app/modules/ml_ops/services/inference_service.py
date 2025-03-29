# import logging
#
# from sqlalchemy.exc import DatabaseError, SQLAlchemyError
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.core.common.exceptions.custom_exceptions import MLServerError
# from app.models.prediction import Prediction
# from app.modules.ml_ops.clients.ml_server_client import MLServerClient
# from app.modules.ml_ops.schemas.inference_api_schema import InferenceRequestSchema
#
# logger = logging.getLogger(__name__)
#
#
# class InferenceService:
#     @staticmethod
#     async def run_inference_and_save(request: InferenceRequestSchema, db: AsyncSession):
#         client = MLServerClient()
#         try:
#             prediction = await client.run_inference(request.stock_name)
#         except Exception as e:
#             logger.error(f"ML inference failed for {request.stock_id}: {e}")
#             raise MLServerError("Failed to get prediction from ML server")
#
#         try:
#             db_prediction = Prediction(
#                 stock_id=prediction.stock_id,
#                 date=prediction.date,
#                 predicted_price=prediction.predicted_price,
#             )
#             db.add(db_prediction)
#             await db.commit()
#         except SQLAlchemyError:
#             logger.exception("Database error while saving prediction")
#             await db.rollback()
#             raise DatabaseError("Failed to save prediction to database")
#
#         return prediction
