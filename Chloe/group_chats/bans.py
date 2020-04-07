import re
from random import randint, sample

import nonebot
from nonebot import CommandSession, on_command, permission

bot = nonebot.get_bot()


@on_command('精致睡眠', permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    context = session.ctx
    bot = session.bot

    group_id = context['group_id']
    user_id = context['user_id']

    await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=28800)


@on_command('解除禁言', aliases=('英雄不朽', ), permission=permission.GROUP_OWNER | permission.GROUP_ADMIN, only_to_me=False)
async def _(session: CommandSession):
    context = session.ctx
    bot = session.bot

    group_id = context['group_id']
    message = context['raw_message']
    self_id = context['self_id']

    group_members = await bot.get_group_member_list(group_id=group_id)
    group_manager = [user['user_id']
                     for user in group_members if user['role'] == 'owner' or user['role'] == 'admin']

    if self_id not in group_manager:
        return

    p = 'CQ:at,qq=(\\d+)]'
    target_id = re.search(p, message)
    if target_id is None:
        return
    target_id = target_id.group(1)

    await bot.set_group_ban(group_id=group_id, user_id=int(target_id), duration=0)


@on_command('一带一路', permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    context = session.ctx
    bot = session.bot

    group_id = context['group_id']
    user_id = context['user_id']
    message = context['raw_message']
    self_id = context['self_id']

    group_members = await bot.get_group_member_list(group_id=group_id)
    group_manager = [user['user_id']
                     for user in group_members if user['role'] == 'owner' or user['role'] == 'admin']

    if self_id not in group_manager:
        return

    p = 'CQ:at,qq=(\\d+)]'
    target_id = re.search(p, message)
    if target_id is None:
        return
    target_id = target_id.group(1)

    ban_time = randint(150, 480)
    await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=ban_time)
    await bot.set_group_ban(group_id=group_id, user_id=int(target_id), duration=ban_time + randint(-120, 60))
    await session.send(f'恭喜[CQ:at,qq={user_id}]成功带动了[CQ:at,qq={target_id}]的经济发展')


@on_command('天降正义', permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    context = session.ctx
    bot = session.bot

    group_id = context['group_id']
    user_id = context['user_id']

    group_members = await bot.get_group_member_list(group_id=group_id)
    group_members = [user['user_id']
                     for user in group_members if user['role'] == 'member']

    targets = sample(group_members, min(len(group_members), 4))
    ban_time = [randint(30, 120), randint(
        30, 120), randint(30, 120), randint(30, 120)]
    await bot.set_group_ban(group_id=group_id, user_id=user_id, duration=(sum(ban_time) + 450))

    for i, target_id in enumerate(targets):
        await bot.set_group_ban(group_id=group_id, user_id=target_id, duration=ban_time[i])
