import json
import math
import os
import random as rd

from nonebot import CommandSession, on_command, permission
from PIL import Image

from .chara import gen_chara_avatar

imgOut = os.path.join(os.path.dirname(__file__), 'out')
if not os.path.exists(imgOut):
    os.mkdir(imgOut)


def load_gacya_config():
    config = json.load(
        open(os.path.join('config', 'gacya.json'), 'r', encoding='utf8'))

    percents = [config['pUp'], config['pFes'], config['p3'], config['p2']]
    pUp = percents[0]
    pFes = pUp + percents[1]
    p3 = pFes + percents[2]
    p2 = p3 + percents[3]

    return [config['gacyaUp'], config['gacyaFes'], config['gacya3'], config['gacya2'], config['gacya1'], pUp, pFes, p3, p2]


def edit_gacya_config(key: str, value):
    config = json.load(
        open(os.path.join('config', 'gacya.json'), 'r', encoding='utf8'))

    config[key] = value
    json.dump(config, open(os.path.join(
        'config', 'gacya.json'), 'w', encoding='utf8'), ensure_ascii=False)


stones = [50, 10, 1]
img_size = 60


@on_command('单抽', aliases=('單抽', ), only_to_me=False)
async def _(session: CommandSession):
    gacyaUp, gacyaFes, gacya3, gacya2, gacya1, pUp, pFes, p3, p2 = load_gacya_config()

    pic = ''
    i = rd.random() * 100
    if i <= pUp:
        pic = gen_chara_avatar(rd.choice(gacyaUp), 3)
    elif i <= pFes:
        pic = gen_chara_avatar(rd.choice(gacyaFes), 3)
    elif i <= p3:
        pic = gen_chara_avatar(rd.choice(gacya3), 3)
    elif i <= p2:
        pic = gen_chara_avatar(rd.choice(gacya2), 2)
    else:
        pic = gen_chara_avatar(rd.choice(gacya1), 1)

    pic.save(os.path.join(imgOut, 's.png'))
    await session.send(f'[CQ:image,file=file:///{os.path.join(imgOut, "s.png")}]', at_sender=True)


@on_command('单抽到up', aliases=('單抽到up', ), only_to_me=False)
async def _(session: CommandSession):
    gacyaUp, gacyaFes, gacya3, _, _, pUp, pFes, p3, p2 = load_gacya_config()

    if pUp == 0:
        await session.finish('当前没有开放up角色')
        return

    result = []
    n3, n2, n1 = [0, 0, 0]

    once_more = True
    while once_more:
        i = rd.random() * 100
        if i <= pUp:
            result.append(rd.choice(gacyaUp))
            n3 += 1
            once_more = False
        elif i <= pFes:
            result.append(rd.choice(gacyaFes))
            n3 += 1
        elif i <= p3:
            result.append(rd.choice(gacya3))
            n3 += 1
        elif i <= p2:
            n2 += 1
        else:
            n1 += 1

    msg = f'花费{n3 + n2 + n1}抽，获得{n3 * stones[0] + n2 * stones[1] + n1 * stones[2]}个无名之石'

    row_nums = math.ceil(pow(n3, 0.5))
    width = row_nums * img_size
    height = math.ceil(n3 / row_nums) * img_size
    background = Image.new('RGB', (width, height), 'white')
    name = session.ctx['user_id']
    for index, cha in enumerate(result):
        pic = gen_chara_avatar(cha, 3).resize((img_size, img_size))
        col = index % row_nums
        row = index // row_nums
        background.paste(pic, (col * img_size, row * img_size))

    output_path = os.path.join(imgOut, f'{name}.png')
    background.save(output_path, quality=100)
    msg += f'\n[CQ:image,file=file:///{output_path}]'
    msg += f'\n共计{n3}个三星，{n2}个两星，{n1}个一星'

    await session.send(msg, at_sender=True)


@on_command('十连抽', aliases=('十連抽', ), only_to_me=False)
async def _(session: CommandSession):
    gacyaUp, gacyaFes, gacya3, gacya2, gacya1, pUp, pFes, p3, p2 = load_gacya_config()

    result = []
    n3, n2, n1 = [0, 0, 0]

    for x in range(10):
        i = rd.random() * 100
        if i <= pUp:
            result.append([rd.choice(gacyaUp), 3])
            n3 += 1
        elif i <= pFes:
            result.append([rd.choice(gacyaFes), 3])
            n3 += 1
        elif i <= p3:
            result.append([rd.choice(gacya3), 3])
            n3 += 1
        elif i <= p2:
            result.append([rd.choice(gacya2), 2])
            n2 += 1
        else:
            if x == 9:
                result.append([rd.choice(gacya2), 2])
                n2 += 1
            else:
                result.append([rd.choice(gacya1), 1])
                n1 += 1

    msg = f'获得{n3 * stones[0] + n2 * stones[1] + n1 * stones[2]}个无名之石'

    background = Image.new('RGB', (img_size * 5, img_size * 2), 'white')
    name = session.ctx['user_id']
    a = 0
    for x in range(5):
        for y in range(2):
            cha, star = result[a]
            pic = gen_chara_avatar(cha, star).resize((img_size, img_size))
            background.paste(pic, (x * img_size, y * img_size))
            a += 1
    output_path = os.path.join(imgOut, f'{name}.png')
    background.save(output_path, quality=100)
    msg += f'[CQ:image,file=file:///{output_path}]'

    await session.send(msg, at_sender=True)


@on_command('抽到up', only_to_me=False)
async def _(session: CommandSession):
    gacyaUp, gacyaFes, gacya3, _, _, pUp, pFes, p3, p2 = load_gacya_config()

    if pUp == 0:
        await session.finish('当前没有开放up角色')
        return

    result = []
    n3, n2, n1 = [0, 0, 0]

    once_more = True
    while once_more:
        for x in range(10):
            i = rd.random() * 100
            if i <= pUp:
                result.append(rd.choice(gacyaUp))
                n3 += 1
                once_more = False
            elif i <= pFes:
                result.append(rd.choice(gacyaFes))
                n3 += 1
            elif i <= p3:
                result.append(rd.choice(gacya3))
                n3 += 1
            elif i <= p2:
                n2 += 1
            else:
                if x == 9:
                    n2 += 1
                else:
                    n1 += 1

    msg = f'花费{n3 + n2 + n1}抽，获得{n3 * stones[0] + n2 * stones[1] + n1 * stones[2]}个无名之石'

    row_nums = math.ceil(pow(n3, 0.5))
    width = row_nums * img_size
    height = math.ceil(n3 / row_nums) * img_size
    background = Image.new('RGB', (width, height), 'white')
    name = session.ctx['user_id']
    for index, cha in enumerate(result):
        pic = gen_chara_avatar(cha, 3).resize((img_size, img_size))
        col = index % row_nums
        row = index // row_nums
        background.paste(pic, (col * img_size, row * img_size))

    output_path = os.path.join(imgOut, f'{name}.png')
    background.save(output_path, quality=100)
    msg += f'\n[CQ:image,file=file:///{output_path}]'
    msg += f'\n共计{n3}个三星，{n2}个两星，{n1}个一星'

    await session.send(msg, at_sender=True)


@on_command('抽一井', only_to_me=False)
async def _(session: CommandSession):
    gacyaUp, gacyaFes, gacya3, _, _, pUp, pFes, p3, p2 = load_gacya_config()

    result = []
    n3, n2, n1 = [0, 0, 0]

    for i in range(30):
        for x in range(10):
            i = rd.random() * 100
            if i <= pUp:
                result.append(rd.choice(gacyaUp))
                n3 += 1
            elif i <= pFes:
                result.append(rd.choice(gacyaFes))
                n3 += 1
            elif i <= p3:
                result.append(rd.choice(gacya3))
                n3 += 1
            elif i <= p2:
                n2 += 1
            else:
                if x == 9:
                    n2 += 1
                else:
                    n1 += 1

    msg = f'花费{n3 + n2 + n1}抽，获得{n3 * stones[0] + n2 * stones[1] + n1 * stones[2]}个无名之石'

    row_nums = math.ceil(pow(n3, 0.5))
    width = row_nums * img_size
    height = math.ceil(n3 / row_nums) * img_size
    background = Image.new('RGB', (width, height), 'white')
    name = session.ctx['user_id']
    for index, cha in enumerate(result):
        pic = gen_chara_avatar(cha, 3).resize((img_size, img_size))
        col = index % row_nums
        row = index // row_nums
        background.paste(pic, (col * img_size, row * img_size))

    output_path = os.path.join(imgOut, f'{name}.png')
    background.save(output_path, quality=100)
    msg += f'\n[CQ:image,file=file:///{output_path}]'
    msg += f'\n共计{n3}个三星，{n2}个两星，{n1}个一星'

    await session.send(msg, at_sender=True)


@on_command('修改up', permission=permission.SUPERUSER, shell_like=True, only_to_me=False)
async def _(session: CommandSession):
    chars = session.argv
    if len(chars) == 0:
        await session.finish('未输入角色。')
        return

    edit_gacya_config('gacyaUp', chars)

    background = Image.new('RGB', (len(chars) * img_size, img_size), 'white')
    for index, cha in enumerate(chars):
        pic = gen_chara_avatar(cha, 3).resize((img_size, img_size))
        background.paste(pic, (index * img_size, 0))
    background.save(os.path.join(imgOut, 's.png'))
    await session.finish('Up角色已修改为\n' + f'[CQ:image,file=file:///{os.path.join(imgOut, "s.png")}]')
