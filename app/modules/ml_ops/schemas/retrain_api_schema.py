from pydantic import BaseModel


class RetrainRequestSchema(BaseModel):
    stock_name: str
