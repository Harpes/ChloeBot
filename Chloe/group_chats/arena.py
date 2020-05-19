import asyncio
import os
import re
import time
from json import loads

import nonebot
from aiohttp import ClientSession
from nonebot import CommandSession, MessageSegment, on_command, permission
from PIL import Image

from .chara import gen_chara_avatar, get_chara_id, get_chara_name

bot = nonebot.get_bot()


# 请自行前往作业网申请key
API_KEY = ''

img_size = 60
imgOut = os.path.join(os.path.dirname(__file__), 'out')
if not os.path.exists(imgOut):
    os.mkdir(imgOut)


async def post_bytes(url, headers=None, data=None):
    async with ClientSession() as asyncsession:
        async with asyncsession.post(url, headers=headers, json=data) as response:
            b = await response.read()
    return b


@on_command('怎么解', only_to_me=False)
async def _(session: CommandSession):
    await search_arena(session)


async def search_arena(session: CommandSession, region: int = 3):
    context = session.ctx
    uid = context['user_id']

    argv = session.current_arg_text.strip()
    argv = re.sub(r'[?？，,_]', ' ', argv)
    argv = argv.split()

    if 0 >= len(argv):
        session.finish('请输入防守方角色，用空格隔开', at_sender=True)
    if 5 < len(argv):
        session.finish('编队不能多于5名角色', at_sender=True)

    defender = [get_chara_id(name) for name in argv]
    for i, id_ in enumerate(defender):
        if id_ == 1000:
            await session.finish(f'编队中含未知角色"{argv[i]}"，请尝试使用官方译名', at_sender=True)

    if len(defender) != len(set(defender)):
        await session.finish('编队中出现重复角色', at_sender=True)

    if session.ctx['message_type'] == 'group':
        await session.bot.set_group_ban(group_id=context['group_id'], user_id=uid, duration=60)

    res = await fetch_arena(defender, region)

    if res['code']:
        print('\n\n', res, '\n\n')
        session.finish('服务器返回数据错误，请联系开发人员')

    resolutions = res['data']['result'][:5]
    nums = len(resolutions)
    if nums < 1:
        session.finish('没有找到解法，请随意解决', at_sender=True)

    msg = '已找到以下解法：\n防守[' + \
        ' '.join([get_chara_name(i) for i in defender]) + ']\n'

    pic = Image.new('RGB', (img_size * 5, img_size * nums), 'white')
    status = 'Like & Dislike:'
    for r, entry in enumerate(resolutions):
        atks = entry['atk']
        for c, a in enumerate(atks):
            charID = a['id'] // 100
            star = a['star']
            equip = a['equip']
            avatar = gen_chara_avatar(get_chara_name(
                charID), star, equip).resize((img_size, img_size))
            pic.paste(avatar, (c * img_size, r * img_size))

        status += f'\n{entry["up"]}/{entry["down"]}'

        comments = entry["comment"]
        if len(comments) > 0:
            status += '：' + comments[0]['msg']

    pic_path = os.path.join(imgOut, f'{uid}.png')
    pic.save(pic_path, quality=100)
    msg += f'[CQ:image,file=file:///{pic_path}]\n' + status
    msg += '\nSupport by pcrdfans_com'
    session.finish(msg, at_sender=True)


async def fetch_arena(defender: list, region: int):
    header = {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36 Edg/81.0.416.72',
        'authorization': API_KEY
    }
    payload = {'_sign': 'a', 'def': [i * 100 + 1 for i in defender], 'nonce': 'a',
               'page': 1, 'sort': 1, 'ts': int(time.time()), 'region': region}
    url = 'https://api.pcrdfans.com/x/v1/search'
    res = await post_bytes(url, header, payload)

    return loads(str(res, 'utf8'))
