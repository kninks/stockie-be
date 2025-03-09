from enum import Enum

from pydantic import BaseModel


class IndustryEnum(str, Enum):
    AGRO_FOOD = "Agro & Food Industry"
    CONSUMER_PRODUCTS = "Consumer Products"
    FINANCIALS = "Financials"
    INDUSTRIALS = "Industrials"
    PROPERTY_CONSTRUCTION = "Property & Construction"
    RESOURCES = "Resources"
    SERVICES = "Services"
    TECHNOLOGY = "Technology"


class PeriodEnum(int, Enum):
    ONE_DAY = 1
    THREE_DAYS = 3
    FIVE_DAYS = 5
    TEN_DAYS = 10
    FIFTEEN_DAYS = 15


class PredictRequestSchema(BaseModel):
    industry: IndustryEnum
    period: PeriodEnum
