from enum import Enum


class IndustryCodeEnum(str, Enum):
    AGRO = "agro_food_industry"
    CONSUMER = "consumer_products"
    FINANCIALS = "financials"
    INDUSTRIALS = "industrials"
    PROPERTY = "property_construction"
    RESOURCES = "resources"
    SERVICES = "services"
    TECH = "technology"
