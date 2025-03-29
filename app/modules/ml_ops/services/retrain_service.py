# from app.modules.ml_ops.clients.ml_server_client import MLServerClient
# from app.modules.ml_ops.schemas.retrain_api_schema import RetrainRequestSchema
#
#
# class RetrainService:
#     @staticmethod
#     async def trigger_retrain(request: RetrainRequestSchema):
#         client = MLServerClient()
#         try:
#             data = await client.retrain_model(request.stock_name)
#             return data
#         except Exception as e:
#             raise e
