import base64
from datetime import datetime, timedelta


def get_start_of_day(target_time: datetime = None) -> datetime:
    target = target_time or datetime.now()
    start = datetime(target.year, target.month, target.day, 5)

    if target > start:
        return start
    else:
        return start - timedelta(days=1)


def encode(id_: int) -> str:
    result = base64.b64encode(bytes(str(id_), 'UTF-8'))
    return str(result, encoding='UTF-8')


def decode(p: str) -> int:
    result = base64.b64decode(bytes(p, 'UTF-8'))
    return int(result)
