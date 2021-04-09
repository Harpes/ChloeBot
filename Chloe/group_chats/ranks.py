import base64
import json
from io import BytesIO
from os import path
from urllib.parse import quote

import requests
from nonebot import CommandSession, on_command, scheduler
from PIL import Image


async def query_rank_sheet_from_yuni(msg: str):
    headers = {
        'Authorization': 'i3pGxk53JoKvBazkT0jY',
        'Queue': quote(msg.strip())
    }
    response = requests.post(
        'https://yuni.lancercmd.cc/api/priconne/query/', headers=headers)
    data = json.loads(response.text)

    return data['layout']


rank_file_list = ['tf.png', 'tm.png', 'tb.png']


@scheduler.scheduled_job('cron', hour=15)
async def _():
    layout = await query_rank_sheet_from_yuni('台前中后rank')
    if len(layout) < 3:
        return

    for i, data in enumerate(layout):
        file_content = data['data']['file'].replace('base64://', '')
        image = Image.open(BytesIO(base64.b64decode(file_content)))
        image.save(path.join(path.dirname(__file__), rank_file_list[i]))


def get_rank_def(filename: str):
    async def temp_func(session: CommandSession):
        filepath = path.join(path.dirname(__file__), filename)
        if path.exists(filepath):
            await session.finish(f'[CQ:image,file=file:///{filepath}]')
        else:
            await session.finish(f'{filename} not found')

    return temp_func


command_list = ['前卫rank', '中卫rank', '后卫rank']
for i, command in enumerate(command_list):
    on_command(command, only_to_me=False)(get_rank_def(rank_file_list[i]))


@on_command('rank', only_to_me=False)
async def _(session: CommandSession):
    paths = [path.join(path.dirname(__file__), i)
             for i in ['Rank1.jpg', 'Rank2.jpg', 'Rank3.jpg']]

    if path.exists(paths[0]):
        cqs = [f'[CQ:image,file=file:///{p}]' for p in paths]
        await session.finish('煌灵' + ''.join(cqs))
    else:
        await session.finish('Rank图未找到')
