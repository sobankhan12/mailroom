from datetime import date, timedelta


def next_send(run_date: str) -> str:
    day = date.fromisoformat(run_date) + timedelta(days=1)
    while day.day != 1:  # walk forward to the 1st of the next month
        day = day + timedelta(days=1)
    while day.weekday() != 0:  # then walk forward to Monday (0)
        day = day + timedelta(days=1)
    return day.isoformat()
