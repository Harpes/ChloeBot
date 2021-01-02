import json
import os
import re
import time

import nonebot
import requests
from nonebot import CommandSession, on_command
from PIL import Image, ImageDraw, ImageFont

from .chara import gen_chara_avatar, get_chara_id, get_chara_name, res_path

bot = nonebot.get_bot()

# https://pcrdfans.com/bot
# 请自行前往作业网申请key
API_KEY = ''

img_size = 60
imgOut = os.path.join(os.path.dirname(__file__), 'out')
if not os.path.exists(imgOut):
    os.mkdir(imgOut)

icon_size = 16
font = ImageFont.truetype('Microsoft Sans Serif.ttf', icon_size)
thumbup = Image.open(os.path.join(res_path, 'gadget', 'thumbup.png')).resize(
    (icon_size, icon_size))
thumbdown = Image.open(os.path.join(
    res_path, 'gadget', 'thumbdown.png')).resize((icon_size, icon_size))


@on_command('怎么解', aliases=('怎么拆', ), only_to_me=False)
async def _(session: CommandSession):
    await search_arena(session, 3)


@on_command('日怎么解', aliases=('日怎么拆', ), only_to_me=False)
async def _(session: CommandSession):
    await search_arena(session, 2)


@on_command('B怎么解', aliases=('B怎么拆', ), only_to_me=False)
async def _(session: CommandSession):
    await search_arena(session, 4)


async def search_arena(session: CommandSession, region: int = 3):
    context = session.ctx
    uid = context['user_id']

    argv = session.current_arg_text.strip()
    argv = re.sub(r'[?？，,_]', ' ', argv)
    argv = argv.split()

    if len(argv) < 1:
        await session.finish('请输入防守方角色，用空格隔开', at_sender=True)
    elif len(argv) < 5:
        await session.finish('当前不支持少于5人的查询，请挪步网页版进行查询', at_sender=True)
    elif len(argv) > 5:
        await session.finish('编队不能多于5名角色', at_sender=True)

    defender = [get_chara_id(name) for name in argv]
    for i, id_ in enumerate(defender):
        if id_ == 1000:
            await session.finish(f'编队中含未知角色"{argv[i]}"，请尝试使用官方译名', at_sender=True)

    if len(defender) != len(set(defender)):
        await session.finish('编队中出现重复角色', at_sender=True)

    res = await fetch_arena(defender, region)

    if not isinstance(res, dict):
        await session.finish('服务器返回错误，请联系开发人员。')

    if res['code']:
        err_code = res['code']
        err_msg = f'服务器返回错误{err_code}，请联系开发人员。'
        print('err response', res)

        if err_code == 117:
            err_msg = '高峰期服务器限流，请挪步网站自行查询。https://pcrdfans.com/battle'
        elif err_code == 103:
            err_msg = 'API Key失效，请联系开发人员。'
        elif err_code == 129:
            err_msg = 'API地址错误，请联系开发人员。'
        elif err_code == 601:
            err_msg = 'IP被ban，请联系开发人员。'

        await session.finish(err_msg)

    if res['data']['result'] is None:
        await session.finish('服务器返回错误0，请稍后重试')

    if len(res['data']['result']) < 1:
        await session.finish('没有找到解法，请随意解决', at_sender=True)

    resolutions = res['data']['result'][:7]
    nums = len(resolutions)

    msg = '已找到以下解法：\n防守[' + \
        ' '.join([get_chara_name(i) for i in defender]) + ']\n'

    pic = Image.new('RGBA', (int(img_size * 6.4), img_size * nums), 'white')
    text_overlay = ImageDraw.Draw(pic)
    # status = 'Like & Dislike:'
    for r, entry in enumerate(resolutions):
        atks = entry['atk']
        sx, sy = 5 * img_size, r * img_size
        for c, a in enumerate(atks):
            charID = a['id'] // 100
            star = a['star']
            equip = a['equip']
            avatar = gen_chara_avatar(
                charID, star, equip).resize((img_size, img_size))
            pic.paste(avatar, (c * img_size, sy))

        gad = 7
        pic.paste(thumbup, (sx + gad, sy + gad), thumbup)
        text_overlay.text(
            (sx + icon_size + gad * 2, sy + gad), str(entry['up']), (0, 0, 0), font=font)
        pic.paste(thumbdown, (sx + gad, sy + icon_size + gad * 3), thumbdown)
        text_overlay.text(
            ((sx + icon_size + gad * 2, sy + icon_size + gad * 3)), str(entry['down']), (0, 0, 0), font=font)

    pic_path = os.path.join(imgOut, f'{uid}.png')
    pic.save(pic_path, quality=100)
    msg += f'[CQ:image,file=file:///{pic_path}]'
    msg += '\nSupport by pcrdfans_com'
    await session.finish(msg, at_sender=True)


async def fetch_arena(defender: list, region: int):
    header = {'authorization': API_KEY}
    payload = {'_sign': 'a', 'def': [int(i) * 100 + 1 for i in defender], 'nonce': 'a',
               'page': 1, 'sort': 1, 'ts': int(time.time()), 'region': region}
    url = 'https://api.pcrdfans.com/x/v1/search'
    response = requests.post(url, json=payload, headers=header)

    res = {}
    try:
        res = json.loads(response.text)
    except BaseException as e:
        print(e)
        res = response

    return res
