from enum import Enum


class IndustryEnum(str, Enum):
    AGRO_FOOD = "agro_food_industry"
    CONSUMER_PRODUCTS = "consumer_products"
    FINANCIALS = "financials"
    INDUSTRIALS = "industrials"
    PROPERTY_CONSTRUCTION = "property_construction"
    RESOURCES = "resources"
    SERVICES = "services"
    TECHNOLOGY = "technology"
