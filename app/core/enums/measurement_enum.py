from enum import Enum


class MeasurementMetric(str, Enum):
    total_predict_time = "total_predict"
    get_data_time = "get_data"
    ml_time = "ml"
    save_time = "save"


class MeasurementTag(str, Enum):
    env = "env"
    batch_size = "batch_size"
    status = "status"

    fail_count = "fail_count"
    success_count = "success_count"


class MeasurementValue(str, Enum):
    local = "local"
    prod = "prod"

    success = "success"
    fail = "fail"
