from random import randint

import nonebot

bot = nonebot.get_bot()


@bot.on_message('group')
async def _(context):
    message = context['raw_message']
    group_id = context['group_id']

    if randint(0, 100) < 4:
        await bot.send_group_msg(group_id=group_id, message=message)


@nonebot.on_notice('group_increase')
async def increase(session: nonebot.NoticeSession):
    # 发送欢迎消息
    user_id = session.ctx['user_id']
    me = session.ctx['self_id']
    # 判断新成员是否是自己
    if user_id != me:
        await session.send(f'欢饮新大佬 [CQ:at,qq={user_id}]')


@nonebot.on_notice('group_decrease')
async def decrease(session: nonebot.NoticeSession):
    # 发送消息
    user_id = str(session.ctx['user_id'])
    operator_id = str(session.ctx['operator_id'])
    if operator_id == user_id:
        inf = await bot.get_stranger_info(user_id=user_id)
        name = inf['nickname']
        await session.send(f'{name}({user_id}) 跑了')
