from json import load
from os import path

KEY_JSON = path.join('config', 'keys.json')


def get_configuration_key(name: str):
    key = ''
    if path.exists(KEY_JSON):
        key = load(open(KEY_JSON, 'r')).get(name, '')
        if len(str(key)) < 1:
            print(f'key配置未找到，请前往config/keys.json填写对应的key [{name}]')
    else:
        print('配置文件不存在，请检查config/keys.json')

    return key
