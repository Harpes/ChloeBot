from importlib import reload
from os import listdir, path, remove

import requests

temp_file_name = '_pcr_nicknames'
cache_folder = path.join(path.dirname(__file__), '__pycache__')


def get_pcr_nickname_data():
    if path.exists(cache_folder):
        files = listdir(cache_folder)
        for file in files:
            if file.startswith(temp_file_name):
                remove(path.join(cache_folder, file))

    resp = requests.get('https://api.akiraxie.cc/pcr/_pcr_data.py')
    if resp.status_code != 200:
        return {}

    data = resp.content
    with open(path.join(path.dirname(__file__), f'{temp_file_name}.py'), 'wb') as pcr_data_file:
        pcr_data_file.write(data)
        pcr_data_file.close()

    from . import _pcr_nicknames
    reload(_pcr_nicknames)

    return _pcr_nicknames.CHARA_NAME
