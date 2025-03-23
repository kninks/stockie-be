from app.modules.ml_ops.clients.ml_server_client import MLServerClient
from app.modules.ml_ops.schemas.retrain_api_schema import RetrainRequestSchema


class RetrainService:
    @staticmethod
    async def trigger_retrain(request: RetrainRequestSchema):
        payload = {"stock_name": request.stock_name}
        try:
            data = await MLServerClient.post("/retrain", data=payload)
            return data
        except Exception as e:
            raise e
