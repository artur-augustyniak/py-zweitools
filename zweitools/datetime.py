#!/usr/bin/env python3

import pytz
from datetime import datetime as dt
from datetime import timedelta as td
from dateutil.parser import parse
import logging

logger = logging.getLogger(__name__)


def tz_now(time_zone: str = "Europe/Warsaw") -> dt:
    return dt.now(tz=pytz.timezone(time_zone))


def date_time_str_lte_now_minus(
    minutes: int,
    date_time: str,
    time_zone: str = "Europe/Warsaw"
) -> bool:
    now = tz_now(time_zone)
    lte_date = now - td(minutes=minutes)
    date_t = parse(date_time)
    return date_t <= lte_date


if __name__ == '__main__':
    logger.critical("This is not the main module")
