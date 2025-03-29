# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.core.common.utils.response_handlers import success_response
# from app.modules.ml_ops.schemas.inference_api_schema import InferenceRequestSchema
# from app.modules.ml_ops.services.inference_service import InferenceService
#
#
# class InferenceController:
#     @staticmethod
#     async def infer(request: InferenceRequestSchema, db: AsyncSession):
#         result = await InferenceService.run_inference_and_save(request, db)
#         return success_response(data=result)
