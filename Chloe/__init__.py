from os import path

import nonebot

MODULES_ON = {
    'clanbattle',
    'group_chats',
    'manager',
}


def init(config) -> nonebot.NoneBot:
    nonebot.init(config)
    bot = nonebot.get_bot()

    for module_name in MODULES_ON:
        module_path = path.join(path.dirname(__file__), module_name)
        nonebot.load_plugins(module_path, f'Chloe.{module_name}')

    return bot


def get_bot() -> nonebot.NoneBot:
    return nonebot.get_bot()
