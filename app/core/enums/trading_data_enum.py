from enum import Enum


class TradingDataEnum(str, Enum):
    CLOSE = "close"
    OPEN = "open"
    HIGH = "high"
    LOW = "low"
    VOLUMES = "volumes"


# def validate_features(features: list[str]) -> list[TradingDataEnum]:
#     validated_features = []
#     for feature in features:
#         try:
#             validated_features.append(TradingDataEnum(feature))  # Convert string to Enum
#         except ValueError:
#             raise ValueError(f"Invalid feature: {feature}")
#     return validated_features
