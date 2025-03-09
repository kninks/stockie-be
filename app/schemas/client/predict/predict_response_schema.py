from pydantic import BaseModel


class RecommendedStockSchema(BaseModel):
    name: str
    predicted_price_upper_bound: float
    predicted_price_lower_bound: float
    is_increase: bool


class OtherStockSchema(BaseModel):
    name: str
    is_increase: bool


class PredictResponseSchema(BaseModel):
    recommended_stock: RecommendedStockSchema
    other_stocks: list[OtherStockSchema]
