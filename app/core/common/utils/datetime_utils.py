from datetime import date, datetime, timedelta
from zoneinfo import ZoneInfo

CLOSED_MARKET_DATES = {
    date(2025, 1, 1),
    date(2025, 2, 12),
    date(2025, 4, 7),
    date(2025, 4, 14),
    date(2025, 4, 15),
    date(2025, 5, 1),
    date(2025, 5, 5),
    date(2025, 5, 12),
    date(2025, 6, 2),
    date(2025, 6, 3),
    date(2025, 7, 10),
    date(2025, 7, 28),
    date(2025, 8, 11),
    date(2025, 8, 12),
    date(2025, 10, 13),
    date(2025, 10, 23),
    date(2025, 12, 5),
    date(2025, 12, 10),
    date(2025, 12, 31),
}


def get_today_bangkok_date() -> datetime.date:
    return datetime.now(ZoneInfo("Asia/Bangkok")).date()


def get_yesterday_bangkok_date() -> datetime.date:
    return datetime.now(ZoneInfo("Asia/Bangkok")).date() - timedelta(days=1)


def get_tomorrow_bangkok_date() -> datetime.date:
    return datetime.now(ZoneInfo("Asia/Bangkok")).date() - timedelta(days=1)


def get_now_bangkok_datetime() -> datetime:
    return datetime.now(ZoneInfo("Asia/Bangkok"))


def is_weekend(d: date) -> bool:
    return d.weekday() >= 5


def is_market_closed(d: date) -> bool:
    return is_weekend(d) or d in CLOSED_MARKET_DATES


def get_next_market_open_date(start_date: date) -> date:
    next_date = start_date + timedelta(days=1)
    while is_market_closed(next_date):
        next_date += timedelta(days=1)
    return next_date


def get_last_market_open_date(start_date: date) -> date:
    last_date = start_date - timedelta(days=1)
    while is_market_closed(last_date):
        last_date -= timedelta(days=1)
    return last_date


def get_n_market_days_ahead(start_date: date, n: int) -> date:
    count = 0
    next_date = start_date
    while count < n:
        next_date += timedelta(days=1)
        if not is_market_closed(next_date):
            count += 1
    return next_date
