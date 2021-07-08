import datetime
from typing import Iterator


def date_days_range(
        start_date: datetime.date,
        end_date: datetime.date,
        is_plus_one: bool = False
) -> Iterator[datetime.date]:
    return date_range(start_date, end_date, is_plus_one, 'days')


def date_hours_range(
        start_date: datetime.date,
        end_date: datetime.date,
        is_plus_one: bool = False
) -> Iterator[datetime.date]:
    return date_range(start_date, end_date, is_plus_one, 'hours')


def date_range(
        start_date: datetime.date,
        end_date: datetime.date,
        is_plus_one: bool = False,
        what: str = None
) -> Iterator[datetime.date]:
    for n in range(
            int(getattr((end_date - start_date), what) + 1 if is_plus_one else 0)
    ):
        yield start_date + datetime.timedelta(**{what: n})
