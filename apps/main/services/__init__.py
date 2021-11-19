import datetime
from typing import Optional

from business_calendar import Calendar, MO, TU, WE, TH, FR


def get_work_days_count(d1: datetime.date, d2: datetime.date) -> Optional[int]:
    return Calendar(workdays=[MO, TU, WE, TH, FR]).busdaycount(d1, d2)
