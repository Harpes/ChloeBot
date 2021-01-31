import json
import math
import os
import random as rd

from nonebot import CommandSession, on_command, permission
from PIL import Image

from .chara import gen_chara_avatar, get_chara_id
from .. import pic2msg


gacya_path = os.path.join('config', 'gacya.json')


def load_gacya_config():
    config = json.load(
        open(gacya_path, 'r', encoding='utf8'))

    percents = [config['up_prob'], config['fes_prob'],
                config['s3_prob'], config['s2_prob']]
    pUp = percents[0]
    pFes = pUp + percents[1]
    p3 = pFes + percents[2]
    p2 = p3 + percents[3]

    return [config['up'], config['fes'], config['star3'], config['star2'], config['star1'], pUp, pFes, p3, p2]


def edit_gacya_config(key: str, value):
    config = json.load(open(gacya_path, 'r', encoding='utf8'))

    config[key] = value
    json.dump(config, open(gacya_path, 'w', encoding='utf8'), ensure_ascii=False)


stones = [50, 10, 1]
img_size = 60


@on_command('单抽', aliases=('單抽', ), only_to_me=False)
async def _(session: CommandSession):
    gacyaUp, gacyaFes, gacya3, gacya2, gacya1, pUp, pFes, p3, p2 = load_gacya_config()

    pic = ''
    i = rd.random() * 1000
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

    await session.send(pic2msg(pic), at_sender=True)


@on_command('单抽到up', aliases=('單抽到up', ), only_to_me=False)
async def _(session: CommandSession):
    gacyaUp, gacyaFes, gacya3, _, _, pUp, pFes, p3, p2 = load_gacya_config()

    if pUp == 0:
        await session.finish('当前没有开放up角色')

    result = []
    n3, n2, n1 = [0, 0, 0]

    once_more = True
    while once_more:
        i = rd.random() * 1000
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

    msg = f'花费{n3 + n2 + n1}抽，获得{n3 * stones[0] + n2 * stones[1] + n1 * stones[2]}个无名之石\n'

    row_nums = math.ceil(pow(n3, 0.5))
    width = row_nums * img_size
    height = math.ceil(n3 / row_nums) * img_size
    background = Image.new('RGB', (width, height), 'white')
    for index, cha in enumerate(result):
        pic = gen_chara_avatar(cha, 3).resize((img_size, img_size))
        col = index % row_nums
        row = index // row_nums
        background.paste(pic, (col * img_size, row * img_size))

    msg += pic2msg(background)
    msg += f'\n共计{n3}个三星，{n2}个两星，{n1}个一星'
    await session.send(msg, at_sender=True)


@on_command('十连抽', aliases=('十連抽', ), only_to_me=False)
async def _(session: CommandSession):
    gacyaUp, gacyaFes, gacya3, gacya2, gacya1, pUp, pFes, p3, p2 = load_gacya_config()

    result = []
    n3, n2, n1 = [0, 0, 0]

    for x in range(10):
        i = rd.random() * 1000
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

    msg = f'获得{n3 * stones[0] + n2 * stones[1] + n1 * stones[2]}个无名之石\n'

    background = Image.new('RGB', (img_size * 5, img_size * 2), 'white')
    a = 0
    for x in range(5):
        for y in range(2):
            cha, star = result[a]
            pic = gen_chara_avatar(cha, star).resize((img_size, img_size))
            background.paste(pic, (x * img_size, y * img_size))
            a += 1

    msg += pic2msg(background)
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
            i = rd.random() * 1000
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

    msg = f'花费{n3 + n2 + n1}抽，获得{n3 * stones[0] + n2 * stones[1] + n1 * stones[2]}个无名之石\n'

    row_nums = math.ceil(pow(n3, 0.5))
    width = row_nums * img_size
    height = math.ceil(n3 / row_nums) * img_size
    background = Image.new('RGB', (width, height), 'white')
    for index, cha in enumerate(result):
        pic = gen_chara_avatar(cha, 3).resize((img_size, img_size))
        col = index % row_nums
        row = index // row_nums
        background.paste(pic, (col * img_size, row * img_size))

    msg += pic2msg(background)
    msg += f'\n共计{n3}个三星，{n2}个两星，{n1}个一星'

    await session.send(msg, at_sender=True)


@on_command('抽一井', only_to_me=False)
async def _(session: CommandSession):
    gacyaUp, gacyaFes, gacya3, _, _, pUp, pFes, p3, p2 = load_gacya_config()

    result = []
    n3, n2, n1 = [0, 0, 0]

    for i in range(30):
        for x in range(10):
            i = rd.random() * 1000
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

    msg = f'花费{n3 + n2 + n1}抽，获得{n3 * stones[0] + n2 * stones[1] + n1 * stones[2]}个无名之石\n'

    row_nums = math.ceil(pow(n3, 0.5))
    width = row_nums * img_size
    height = math.ceil(n3 / row_nums) * img_size
    background = Image.new('RGB', (width, height), 'white')
    for index, cha in enumerate(result):
        pic = gen_chara_avatar(cha, 3).resize((img_size, img_size))
        col = index % row_nums
        row = index // row_nums
        background.paste(pic, (col * img_size, row * img_size))

    msg += pic2msg(background)
    msg += f'\n共计{n3}个三星，{n2}个两星，{n1}个一星'

    await session.send(msg, at_sender=True)


@on_command('修改up', permission=permission.SUPERUSER, shell_like=True, only_to_me=False)
async def _(session: CommandSession):
    chars = session.argv
    if len(chars) == 0:
        await session.finish('未输入角色。')
        return

    char_ids = [get_chara_id(name) for name in chars]
    edit_gacya_config('up', char_ids)

    background = Image.new('RGB', (len(chars) * img_size, img_size), 'white')
    for index, cha in enumerate(char_ids):
        pic = gen_chara_avatar(cha, 3).resize((img_size, img_size))
        background.paste(pic, (index * img_size, 0))

    await session.finish('Up角色已修改为\n' + pic2msg(background))


@on_command('修改概率', permission=permission.SUPERUSER, shell_like=True, only_to_me=False)
async def _(session: CommandSession):
    probs = session.argv
    if len(probs) == 0:
        await session.finish('未输入概率。')
        return

    prob_indexs = ['up_prob', 'fes_prob', 's3_prob', 's2_prob']
    for i, prob in enumerate(probs):
        edit_gacya_config(prob_indexs[i], int(prob))

    _, _, _, _, _, pUp, pFes, p3, p2 = load_gacya_config()
    pUp, pFes, p3, p2 = map(lambda x: x / 10, [pUp, pFes, p3, p2])
    await session.finish('当前抽卡概率为: up%.1f%%, fes%.1f%%, 三星%.1f%%, 两星%.1f%%' % (pUp, pFes - pUp, p3 - pFes, p2 - p3))
