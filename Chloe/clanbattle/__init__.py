import json
import os
import re
from datetime import datetime

from nonebot import CommandSession, MessageSegment, on_command, permission

from .battleMaster import BattleMaster

__plugin_name__ = 'clanbattle'

boss_names = ['一王', '二王', '三王', '四王', '五王']
reservations_folder = 'reservations'
if not os.path.exists(reservations_folder):
    os.mkdir(reservations_folder)

battleObj = BattleMaster()


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
