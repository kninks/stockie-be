from datetime import datetime
from zoneinfo import ZoneInfo


def get_today_bangkok_date() -> datetime.date:
    return datetime.now(ZoneInfo("Asia/Bangkok")).date()


def get_now_bangkok_datetime() -> datetime:
    return datetime.now(ZoneInfo("Asia/Bangkok"))
