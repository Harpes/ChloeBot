import os
import random as rd

import nonebot
from nonebot import CommandSession, on_command
from PIL import Image

imgRoot = os.path.join(os.path.dirname(__file__), 'image')
os.chdir(imgRoot)

gacya3 = ['杏奈', '真步', '璃乃',
          '初音', '霞', '伊緒',
          '咲戀', '望', '妮諾', '秋乃',
          '鏡華', '智', '真琴',
          '伊莉亞', '純', '靜流',
          '莫妮卡', '流夏',
          #   '吉塔',
          #   '亞里莎',
          '安', '古蕾婭',
          '空花（大江戶）', '妮諾（大江戶）', '碧（插班生）',
          '克蘿依']

gacya2 = ['茉莉', '茜里', '宮子',
          '雪', '七七香', '美里',
          '鈴奈', '香織', '美美',
          '綾音', '鈴', '惠理子',
          '忍', '真陽', '栞',
          '千歌', '空花', '珠希',
          '美冬', '深月', '紡希']

gacya1 = ['日和', '怜', '禊', '胡桃', '依里', '鈴莓', '優花梨', '碧', '美咲', '莉瑪', '步未']

gacyaFes = ['矛依未', '克莉絲提娜', 'ネネカ']

gacyaUp = ['亞里莎', '吉塔']

stones = [50, 10, 1]

# up, FES, 3星, 2星
percents = [0.7, 0, 1.8, 20.5]  # 普通
# percents = [1.4, 0, 3.6, 18]  # up双倍
# percents = [0.7, 0.6, 4.3, 18]  # FES三星双倍

pUp = percents[0]
pFes = pUp + percents[1]
p3 = pFes + percents[2]
p2 = p3 + percents[3]


@on_command('单抽', only_to_me=False)
async def _(session: CommandSession):
    msg = ''
    if session.ctx['message_type'] == 'group':
        msg = '[CQ:at,qq={}] '.format(str(session.ctx['user_id']))

    pic = ''
    i = rd.random() * 100
    if i <= pUp:
        pic = rd.choice(gacyaUp)
    elif i <= pFes:
        pic = rd.choice(gacyaFes)
    elif i <= p3:
        pic = rd.choice(gacya3)
    elif i <= p2:
        pic = rd.choice(gacya2)
    else:
        pic = rd.choice(gacya1)

    pic = f'[CQ:image,file=file:///{imgRoot}\\{pic}.png]'

    await session.send(msg + pic)


@on_command('十连抽', only_to_me=False)
async def _(session: CommandSession):
    result = []
    n3, n2, n1 = [0, 0, 0]

    msg = ''
    if session.ctx['message_type'] == 'group':
        context = session.ctx
        await session.bot.set_group_ban(group_id=context['group_id'], user_id=context['user_id'], duration=30)
        msg = '[CQ:at,qq={}] '.format(str(context['user_id']))

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
            result.append(rd.choice(gacya2))
            n2 += 1
        else:
            if x == 9:
                result.append(rd.choice(gacya2))
                n2 += 1
            else:
                result.append(rd.choice(gacya1))
                n1 += 1

    msg += f'获得{n3 * stones[0] + n2 * stones[1] + n1 * stones[2]}个无名之石'

    background = Image.new('RGBA', (312, 126), color='lavenderblush')
    name = session.ctx['user_id']
    a = 0
    for x in range(5):
        for y in range(2):
            pic = Image.open(result[a] + '.png')
            background.paste(pic, (x * 62 + 2, y * 62 + 2))
            a += 1
    background.save(imgRoot + f'\\out\\{name}.png')

    await session.send(msg + f'[CQ:image,file=file:///{imgRoot}\\out\\{name}.png]')


@on_command('抽一井', only_to_me=False)
async def _(session: CommandSession):
    result = []
    n3, n2, n1 = [0, 0, 0]

    msg = ''
    if session.ctx['message_type'] == 'group':
        context = session.ctx
        await session.bot.set_group_ban(group_id=context['group_id'], user_id=context['user_id'], duration=40)
        msg = '[CQ:at,qq={}] '.format(str(context['user_id']))

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

    msg += f'获得{n3 * stones[0] + n2 * stones[1] + n1 * stones[2]}个无名之石'

    name = session.ctx['user_id']
    newPic = Image.new('RGBA', (n3 * 62 + 2, 64), color='lavenderblush')
    for x in range(n3):
        pic = Image.open(result[x] + '.png')
        newPic.paste(pic, (x * 62 + 2, 2))
    newPic.save(imgRoot + f'\\out\\{name}.png')
    msg += f'[CQ:image,file=file:///{imgRoot}\\out\\{name}.png]'

    msg += f'\n共计{n3}个三星，{n2}个两星，{n1}个一星'

    await session.send(msg)
