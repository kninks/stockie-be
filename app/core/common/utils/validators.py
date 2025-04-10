import logging
from typing import Any, Dict, List, Set

from app.core.common.exceptions.custom_exceptions import ResourceNotFoundError

logger = logging.getLogger(__name__)


__all__ = [
    "validate_required",
    "validate_enum_input",
    "validate_entity_exists",
    "validate_exact_length",
    "sanitize_batch",
    "normalize_stock_ticker",
    "normalize_stock_tickers",
    "normalize_stock_tickers_in_data",
]


def validate_required(value, name: str):
    """
    Validates that the input (single or list) is not None or empty.

    # Validate required string input
    validate_required(stock_ticker, "stock ticker")

    # Validate non-empty list
    validate_required(industry_codes, "industry codes")
    """

    if value is None:
        logger.error(f"No {name} provided")
        raise ValueError(f"No {name} provided")

    if isinstance(value, str) and not value.strip():
        logger.error(f"No {name} provided (empty string)")
        raise ValueError(f"No {name} provided")

    if isinstance(value, (list, set, tuple)) and len(value) == 0:
        logger.error(f"No {name} provided (empty collection)")
        raise ValueError(f"No {name} provided")


def validate_enum_input(input_value, enum_type: type, name: str = "input"):
    """
    Validates that the input (single enum or list of enums) are valid instances.

    # Validate a single industry code
    validate_enum_input(industry_code, IndustryCodeEnum, "industry code")

    # Validate a list of industry codes
    validate_enum_input(industry_codes, IndustryCodeEnum, "industry codes")
    """

    if input_value is None:
        raise ValueError(f"No {name} provided")

    if isinstance(input_value, list):
        if not input_value:
            raise ValueError(f"No {name} values provided")
        if not all(isinstance(val, enum_type) for val in input_value):
            raise ValueError(f"All {name} values must be of type {enum_type.__name__}")
    else:
        if not isinstance(input_value, enum_type):
            raise ValueError(f"{name} must be of type {enum_type.__name__}")


def validate_entity_exists(entity, name: str):
    """
    Validates that the entity (single or list) exists and is not None or empty.

    # Validate a fetched single DB record
    validate_entity_exists(stock, "Stock")

    # Validate a non-empty list of predictions
    validate_entity_exists(predictions, "Predictions")
    """

    if not entity:
        logger.error(f"{name} not found.")
        raise ResourceNotFoundError(f"{name} not found.")


def validate_exact_length(collection, expected_len: int, name: str):
    """
    Validates that the collection (list or set) has an exact length.

    # Validate exactly 5 predictions were returned
    validate_exact_length(predictions, 5, "predictions")

    # Validate 40 active stocks
    validate_exact_length(stocks, 40, "active stocks")
    """

    if len(collection) != expected_len:
        logger.error(f"Expected {expected_len} {name}, found {len(collection)}.")
        raise ResourceNotFoundError(
            f"Expected {expected_len} {name}, found {len(collection)}."
        )


def strip_unwanted_fields(
    data: Dict[str, Any], fields_to_strip: Set[str]
) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if k not in fields_to_strip}


def keep_only_allowed_fields(
    data: Dict[str, Any], allowed_fields: Set[str]
) -> Dict[str, Any]:
    return {k: v for k, v in data.items() if k in allowed_fields}


def sanitize_batch(
    data_list: List[Dict[str, Any]],
    *,
    allowed_fields: Set[str] = None,
    fields_to_strip: Set[str] = None,
) -> List[Dict[str, Any]]:
    sanitized = []
    for data in data_list:
        if allowed_fields:
            sanitized.append(keep_only_allowed_fields(data, allowed_fields))
        elif fields_to_strip:
            sanitized.append(strip_unwanted_fields(data, fields_to_strip))
        else:
            sanitized.append(data)
    return sanitized


def normalize_stock_ticker(ticker: str) -> str:
    return ticker.strip().upper()


def normalize_stock_tickers(tickers: List[str]) -> List[str]:
    return [normalize_stock_ticker(t) for t in tickers]


def normalize_stock_tickers_in_data(data_list: List[dict]) -> List[dict]:
    for item in data_list:
        item["stock_ticker"] = normalize_stock_ticker(item["stock_ticker"])
    return data_list
