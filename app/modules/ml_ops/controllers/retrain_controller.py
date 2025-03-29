# from app.core.common.utils.response_handlers import success_response
# from app.modules.ml_ops.schemas.retrain_api_schema import RetrainRequestSchema
# from app.modules.ml_ops.services.retrain_service import RetrainService
#
#
# class RetrainController:
#     @staticmethod
#     async def retrain(request: RetrainRequestSchema):
#         try:
#             result = await RetrainService.trigger_retrain(request)
#             return success_response(data=result)
#         except Exception as e:
#             raise e
