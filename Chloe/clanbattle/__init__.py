import json
import os
import re
from datetime import datetime, timedelta

import nonebot
from nonebot import CommandSession, MessageSegment, on_command, permission

from .battleMaster import BattleMaster

__plugin_name__ = 'clanbattle'

boss_names = ['', '一王', '二王', '三王', '四王', '五王']
reservations_folder = 'reservations'
if not os.path.exists(reservations_folder):
    os.mkdir(reservations_folder)

bot = nonebot.get_bot()
battleObj = BattleMaster()


def get_start_of_day() -> datetime:
    now = datetime.now()
    start = datetime(now.year, now.month, now.day, 5)

    if now > start:
        return start
    else:
        return start - timedelta(days=1)


async def get_member_name(gid: int, uid: int) -> str:
    member_info = await bot.get_group_member_info(group_id=gid, user_id=uid)
    name = member_info['card'].strip()
    if not name:
        name = member_info['nickname'].strip()

    return name or str(uid)


async def add_clan(session: CommandSession, server: int):
    gid = session.ctx['group_id']
    # TODO
    name = '公会名'

    clan = battleObj.get_clan(gid)
    if clan is None:
        battleObj.add_clan(gid, name, server)
    else:
        await session.finish('创建公会失败，当前群已有公会' + clan[0])

    clan = battleObj.get_clan(gid)
    if clan is None:
        await session.finish('创建公会失败')
    else:
        await session.finish('创建%s服公会[%s]成功' % (['日', '台', '国'][clan[1]], clan[0]))


@on_command('添加日服公会', permission=permission.GROUP_OWNER, shell_like=True, only_to_me=False)
async def add_clan_jp(session: CommandSession):
    await add_clan(session, 0)


@on_command('添加台服公会', permission=permission.GROUP_OWNER, shell_like=True, only_to_me=False)
async def add_clan_cntw(session: CommandSession):
    await add_clan(session, 1)


@on_command('添加国服公会', permission=permission.GROUP_OWNER, shell_like=True, only_to_me=False)
async def add_clan_cn(session: CommandSession):
    await add_clan(session, 2)


@on_command('会战进度', aliases=('状态', ), permission=permission.GROUP, only_to_me=False)
async def show_progress(session: CommandSession):
    gid = session.ctx['group_id']

    clan, r, boss, hp = battleObj.get_current_state(gid)

    if clan is None:
        await session.finish('当前群没有创建公会')
    else:
        await session.finish('当前%d周目%s，剩余血量%s' % (r, boss_names[boss], '{:,}'.format(hp)))


def add_rec(gid: int, uid: int, r: int, boss: int, dmg: int, flag: int = 0):
    battleObj.add_rec(gid, uid, r, boss, dmg, flag)
    return battleObj.get_current_state(gid)


async def update_rec(gid: int, uid: int, dmg: int):
    msg = ''
    rec_type = 0

    member_name = battleObj.get_member_name(gid, uid)
    if member_name is None:
        battleObj.add_member(gid, uid, await get_member_name(gid, uid))
        member_name = battleObj.get_member_name(gid, uid)

    msg += member_name

    _, prev_round, prev_boss, prev_hp = battleObj.get_current_state(gid)
    if dmg > prev_hp:
        await bot.send_group_msg(group_id=gid, message='伤害超过当前BOSS剩余血量，请修正。')
        return
    if dmg == -1 or dmg == prev_hp:
        rec_type = 1
        dmg = prev_hp

    msg += '对%d周目%s造成了%s伤害' % (prev_round,
                               boss_names[prev_boss], '{:,}'.format(prev_hp))

    member_recs = battleObj.get_rec(gid, uid, get_start_of_day())
    member_today_rec_num, flag = 0, 0
    for rec in member_recs:
        flag = rec['flag']
        if flag == 0:
            member_today_rec_num += 1
        elif flag == 2:
            member_today_rec_num += 1

    dmg_type, new_flag = '完整刀', rec_type
    if flag == 0 or flag == 2:
        dmg_type = ['完整刀', '尾刀'][rec_type]
    else:
        # flag = 1
        dmg_type = ['余刀', '余尾刀'][rec_type]
        new_flag = 2

    msg += '(今日第%d刀，%s)' % (member_today_rec_num + 1, dmg_type)

    msg += '\n----------\n'
    _, after_round, after_boss, after_hp = add_rec(
        gid, uid, prev_round, prev_boss, dmg, new_flag)
    msg += '当前%d周目%s，剩余血量%s' % (after_round,
                                boss_names[after_boss], '{:,}'.format(after_hp))

    await bot.send_group_msg(group_id=gid, message=msg)


@bot.on_message('group')
async def handle_rec(context):
    message = context['raw_message']
    gid = context['group_id']
    uid = context['user_id']

    clan = battleObj.get_clan(gid)
    if clan is None:
        return

    dmg = 0

    dmg_report1 = re.match(r'^报刀 ?(\d+) *$', message)
    dmg_report2 = re.match(r'^(?:\[CQ:at,qq=(\d+)\]) ?(\d+) *$', message)
    kill_report1 = re.match(r'^尾刀 ?(?:\[CQ:at,qq=(\d+)\])? *$', message)
    kill_report2 = re.match(r'^(?:\[CQ:at,qq=(\d+)\]) ?尾刀$', message)

    if dmg_report1:
        dmg = int(dmg_report1.group(1))
    elif dmg_report2:
        uid = dmg_report2.group(1)
        dmg = int(dmg_report2.group(2))
    elif kill_report1:
        dmg = -1
        if kill_report1.group(1):
            uid = kill_report1.group(1)
    elif kill_report2:
        dmg = -1
        if kill_report2.group(1):
            uid = kill_report2.group(1)
    else:
        return

    await update_rec(gid, uid, dmg)
