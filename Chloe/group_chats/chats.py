import os
import random

import nonebot
from nonebot import CommandSession, NoticeSession, on_command, on_notice

bot = nonebot.get_bot()


@bot.on_message('group')
async def _(context):
    message = context['raw_message']
    group_id = context['group_id']
    if len(message) > 20:
        return

    if random.randint(0, 100) < 3:
        await bot.send_group_msg(group_id=group_id, message=message)


@on_notice('group_increase')
async def increase(session: NoticeSession):
    # 发送欢迎消息
    user_id = session.ctx['user_id']
    me = session.ctx['self_id']
    # 判断新成员是否是自己
    if user_id != me:
        await session.send(f'欢饮新大佬 [CQ:at,qq={user_id}]')


@on_notice('group_decrease')
async def decrease(session: NoticeSession):
    # 发送消息
    user_id = str(session.ctx['user_id'])
    operator_id = str(session.ctx['operator_id'])
    if operator_id == user_id:
        inf = await bot.get_stranger_info(user_id=user_id)
        name = inf['nickname']
        await session.send(f'{name}({user_id}) 跑了')


@on_command('前卫rank')
async def _(session: CommandSession):
    path = os.path.join(os.path.dirname(__file__), "RF.png")
    await session.send(f'無羽R17-4[CQ:image,file=file:///{path}]')


@on_command('中卫rank')
async def _(session: CommandSession):
    path = os.path.join(os.path.dirname(__file__), "RM.png")
    await session.send(f'無羽R17-4[CQ:image,file=file:///{path}]')


@on_command('后卫rank')
async def _(session: CommandSession):
    path = os.path.join(os.path.dirname(__file__), "RB.png")
    await session.send(f'無羽R17-4[CQ:image,file=file:///{path}]')


@on_command('rank')
async def _(session: CommandSession):
    path = os.path.join(os.path.dirname(__file__), "Rank.png")
    await session.send(f'煌灵R17-4[CQ:image,file=file:///{path}]')

    # path1 = os.path.join(os.path.dirname(__file__), "Rank1.png")
    # path2 = os.path.join(os.path.dirname(__file__), "Rank2.png")
    # path3 = os.path.join(os.path.dirname(__file__), "Rank3.png")
    # await session.send(f'煌灵R17-3[CQ:image,file=file:///{path1}][CQ:image,file=file:///{path2}][CQ:image,file=file:///{path3}]')


@on_command('黄骑充电')
async def _(session: CommandSession):
    path = os.path.join(os.path.dirname(__file__), "黄骑充电.jpg")
    await session.send(f'[CQ:image,file=file:///{path}]')
