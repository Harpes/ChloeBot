import base64
import json
import os
from datetime import datetime, timedelta

DB_folder = 'clanbattle'
CLAN_CONFIGS = os.path.join(DB_folder, 'groups.json')
if not os.path.exists(DB_folder):
    os.mkdir(DB_folder)


def get_configs() -> dict:
    if os.path.exists(CLAN_CONFIGS):
        return json.load(open(CLAN_CONFIGS, 'r'))
    return {}


def save_configs(configs: dict):
    json.dump(configs, open(CLAN_CONFIGS, 'w'))


def add_clan(gid: int, name: str, server: int):
    configs = get_configs()
    configs[str(gid)] = [name, server]
    save_configs(configs)


def get_clan(gid: int) -> [str, int]:
    return get_configs().get(str(gid), [None, -1])


def del_clan(gid: int):
    configs = get_configs()
    if str(gid) in configs:
        del configs[str(gid)]
    save_configs(configs)


def get_month(target_time: datetime = None) -> str:
    target = target_time or datetime.now()
    day = target - timedelta(hours=5)
    if day.day < 20:
        day -= timedelta(days=day.day)

    return day.strftime("%Y%m")


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
