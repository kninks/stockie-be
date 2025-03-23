from pydantic import BaseModel


class TopStockRepoSchema(BaseModel):
    stock_name: str
    predicted_price_upper_bound: float
    predicted_price_lower_bound: float
