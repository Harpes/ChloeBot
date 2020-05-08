import json
import os
import re
from datetime import datetime, timedelta
from random import choices

import nonebot
from nonebot import CommandSession, MessageSegment, on_command, permission

from .battleMaster import BattleMaster

__plugin_name__ = 'clanbattle'

server_http_adress = 'http://localhost:8000'

boss_names = ['树上', '一王', '二王', '三王', '四王', '五王']
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
    name = battleObj.get_member_name(gid, uid)
    if name is not None:
        return name

    member_info = await bot.get_group_member_info(group_id=gid, user_id=uid)
    name = member_info['card'].strip()
    if not name:
        name = member_info['nickname'].strip()

    return name or str(uid)


async def add_clan(session: CommandSession, server: int):
    gid = session.ctx['group_id']
    name = session.argv[0] or str(gid)

    clan = battleObj.get_clan(gid)
    if clan is None:
        battleObj.add_clan(gid, name, server)
    else:
        await session.finish(f'创建公会失败，当前群已有公会[{clan[0]}]')

    clan = battleObj.get_clan(gid)
    if clan is None:
        await session.finish('创建公会失败')
    else:
        await session.finish('创建%s服公会[%s]成功' % (['日', '台', '国'][clan[1]], clan[0]))


@on_command('创建日服公会', permission=permission.GROUP_OWNER, shell_like=True, only_to_me=False)
async def add_clan_jp(session: CommandSession):
    await add_clan(session, 0)


@on_command('创建台服公会', permission=permission.GROUP_OWNER, shell_like=True, only_to_me=False)
async def add_clan_cntw(session: CommandSession):
    await add_clan(session, 1)


@on_command('创建国服公会', permission=permission.GROUP_OWNER, shell_like=True, only_to_me=False)
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


@on_command('报告', aliases=('出刀统计', '每日报告'), permission=permission.GROUP, only_to_me=False)
async def show_report(session: CommandSession):
    gid = session.ctx['group_id']

    clan = battleObj.get_clan(gid)
    if clan is None:
        return
    server = clan[1]

    recs = battleObj.get_rec(gid, uid=None, time=get_start_of_day())
    if len(recs) == 0:
        await session.finish('今日尚无出刀记录。')
        return

    # 整刀数 尾刀数
    whole_nums, half_nums = 0, 0
    rec_rows = []
    member_name = {}
    for rec in recs:
        uid, time, r, boss, dmg, flag = [rec[i] for i in [
            'uid', 'time', 'round', 'boss', 'dmg', 'flag']]

        # if flag in [0, 2, 3]:
        #     rec_nums += 1
        if flag == 0:
            whole_nums += 1
        elif flag == 1:
            half_nums += 1
        else:
            whole_nums += 1
            half_nums -= 1

        value = {'uid': uid, 'time': time,
                 'round': r, 'boss': boss, 'dmg': dmg, 'flag': flag}

        if uid not in member_name:
            name = await get_member_name(gid, uid)
            member_name[uid] = name
        name = member_name[uid]
        value['user_name'] = name

        score = battleObj.get_score_rate(r, boss, server) * dmg
        value['score'] = score

        stage = ['A', 'B', 'C', 'D'][battleObj.get_stage(r) - 1]
        rec_type = ['完整刀', '尾刀', '余刀', '余尾刀'][flag]
        value['type'] = stage + str(boss) + rec_type

        rec_rows.append(value)

    msg = '今日已出%s完整刀。' % (whole_nums, )
    if half_nums != 0:
        msg = msg.replace("。", "，%s尾刀。" % (half_nums, ))

    try:
        file_name = str(gid) + datetime.now().strftime('%m%d%H')
        out_data_path = os.path.join(
            os.path.dirname(__file__), 'report', 'data', file_name + '.json')
        json.dump(rec_rows, open(out_data_path, 'w',
                                 encoding='utf-8'), ensure_ascii=False)

        msg += '\n详情：' + server_http_adress + '?' + file_name
    except:
        print('some err happened')
        pass

    await session.finish(msg)


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
        hp = '{:,}'.format(prev_hp)
        await bot.send_group_msg(group_id=gid, message=f'伤害超过当前BOSS剩余血量{hp}，请修正。')
        return
    if dmg == -1 or dmg == prev_hp:
        rec_type = 1
        dmg = prev_hp

    msg += '对%d周目%s造成了%s伤害' % (prev_round,
                               boss_names[prev_boss], '{:,}'.format(dmg))

    member_recs = battleObj.get_rec(gid, uid, get_start_of_day())
    member_today_rec_nums, flag = 0, 0
    for rec in member_recs:
        flag = rec['flag']
        if flag in [0, 2, 3]:
            member_today_rec_nums += 1

    dmg_type, new_flag = '完整刀', rec_type
    if flag in [0, 2, 3]:
        dmg_type = ['完整刀', '尾刀'][rec_type]
    else:
        # flag = 1
        dmg_type = ['余刀', '余尾刀'][rec_type]
        new_flag = 2 + rec_type

    msg += '(今日第%d刀，%s)' % (member_today_rec_nums + 1, dmg_type)

    msg += '\n----------\n'
    _, after_round, after_boss, after_hp = add_rec(
        gid, uid, prev_round, prev_boss, dmg, new_flag)
    msg += '当前%d周目%s，剩余血量%s' % (after_round,
                                boss_names[after_boss], '{:,}'.format(after_hp))

    if prev_boss != after_boss:
        on_tree = call_reserve(gid, 0)
        if len(on_tree) > 0:
            msg += f'\n----------\n可以下树了{on_tree}'

        on_reverse = call_reserve(gid, after_boss)
        if len(on_reverse) > 0:
            msg += f'\n----------\n{boss_names[after_boss]}已经出现{on_reverse}'

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

    dmg_report1 = re.match(r'^[报報]刀 ?(\d+) *$', message)
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


@on_command('撤销', permission=permission.GROUP, only_to_me=False)
async def undo_rec(session: CommandSession):
    context = session.ctx
    gid = context['group_id']
    uid = context['user_id']
    auth = context['sender']['role']

    clan = battleObj.get_clan(gid)
    if clan is None:
        return

    recs = battleObj.get_rec(gid, uid=None, time=get_start_of_day())
    if len(recs) == 0:
        await session.finish('今日尚无出刀记录。')
        return

    last_rec = recs[-1]
    recid, last_uid, r, boss, dmg = [last_rec[i]
                                     for i in ['recid', 'uid', 'round', 'boss', 'dmg']]
    if last_rec['uid'] != uid and auth == 'member':
        await session.finish('撤回别人的出刀记录需要管理权限。')
        return

    u_name = await get_member_name(gid, last_uid)

    msg = '已撤销%s对%s周目%s的%s伤害\n----------\n' % (
        u_name, r, boss_names[boss], '{:,}'.format(dmg))
    battleObj.delete_rec(gid, recid)
    _, r, boss, hp = battleObj.get_current_state(gid)
    msg += '当前%d周目%s，剩余血量%s' % (r, boss_names[boss], '{:,}'.format(hp))

    await session.finish(msg)


psw = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
psw = ''.join(choices(psw, k=6))
@on_command('清空会战记录', aliases=('清除会战记录', '重置进度', '重置会战进度'), permission=permission.GROUP_OWNER | permission.GROUP_ADMIN, only_to_me=False)
async def clear_rec(session: CommandSession):
    msg = session.get('message', prompt=f'请回复[{psw}]以重置会战进度').strip()
    if msg == psw:
        gid = session.ctx['group_id']
        battleObj.clear_rec(gid)

        await show_progress(session)


def add_reserve(gid: int, uid: int, boss: int) -> str:
    # 0：树，1-5：BOSS
    reservation_path = os.path.join(reservations_folder, f'{gid}.json')
    reservation = {}
    if os.path.exists(reservation_path):
        reservation = json.load(open(reservation_path, 'r'))
    reservation_list = reservation.get(str(boss), [])

    if uid in reservation_list:
        if boss == 0:
            return f'{str(MessageSegment.at(uid))} 你已上树'
        return f'{str(MessageSegment.at(uid))} 你已预约过{boss_names[boss]}，请勿重复预约'
    else:
        reservation_list.append(uid)
        reservation[str(boss)] = reservation_list
        json.dump(reservation, open(reservation_path, 'w'))

        if boss == 0:
            return f'{str(MessageSegment.at(uid))} 成功上树，当前树上人：{len(reservation_list)}'
        return f'{str(MessageSegment.at(uid))} 你已成功预约{boss_names[boss]}，当前Boss预约人数：{len(reservation_list)}'


def cancel_reserve(gid: int, uid: int, boss: int) -> str:
    reservation_path = os.path.join(reservations_folder, f'{gid}.json')
    reservation = {}
    if os.path.exists(reservation_path):
        reservation = json.load(open(reservation_path, 'r'))
    reservation_list = reservation.get(str(boss), [])

    if uid in reservation_list:
        reservation_list.remove(uid)
        reservation[str(boss)] = reservation_list
        json.dump(reservation, open(reservation_path, 'w'))

        if boss == 0:
            return f'{str(MessageSegment.at(uid))} 你已下树'
        return f'{str(MessageSegment.at(uid))} 已为你取消预约{boss_names[boss]}'
    else:
        if boss == 0:
            return f'{str(MessageSegment.at(uid))} 你尚未上树'
        return f'{str(MessageSegment.at(uid))} 你尚未预约{boss_names[boss]}'


async def see_reserve(gid: int, boss: int) -> list:
    reservation_path = os.path.join(reservations_folder, f'{gid}.json')
    reservation = {}
    if os.path.exists(reservation_path):
        reservation = json.load(open(reservation_path, 'r'))
    reservation_list = reservation.get(str(boss), [])

    msg = boss_names[boss] + f' {len(reservation_list)}人'
    if len(reservation_list) > 0:
        name_list = []
        for uid in reservation_list:
            member_name = await get_member_name(gid, uid)
            name_list.append(member_name)

        msg += f"：{'、'.join(name_list)}"

    return msg


def call_reserve(gid: int, boss: int) -> str:
    reservation_path = os.path.join(reservations_folder, f'{gid}.json')
    reservation = {}
    if os.path.exists(reservation_path):
        reservation = json.load(open(reservation_path, 'r'))
    reservation_list = reservation.get(str(boss), [])
    reservation[str(boss)] = []
    json.dump(reservation, open(reservation_path, 'w'))

    msg = ''
    for uid in reservation_list:
        msg += str(MessageSegment.at(uid))

    return msg


async def reserve(session: CommandSession, boss: int):
    context = session.ctx
    gid = context['group_id']
    uid = context['user_id']

    clan = battleObj.get_clan(gid)
    if clan is None:
        return

    msg = add_reserve(gid, uid, boss)
    await session.finish(msg)


async def unreserve(session: CommandSession, boss: int):
    context = session.ctx
    gid = context['group_id']
    uid = context['user_id']

    clan = battleObj.get_clan(gid)
    if clan is None:
        return

    msg = cancel_reserve(gid, uid, boss)
    await session.finish(msg)


@on_command('预约1', aliases=('预约一', '预约一王'), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    await reserve(session, 1)


@on_command('预约2', aliases=('预约二', '预约二王'), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    await reserve(session, 2)


@on_command('预约3', aliases=('预约三', '预约三王'), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    await reserve(session, 3)


@on_command('预约4', aliases=('预约四', '预约四王'), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    await reserve(session, 4)


@on_command('预约5', aliases=('预约五', '预约五王'), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    await reserve(session, 5)


@on_command('取消1', aliases=('取消一', ), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    await unreserve(session, 1)


@on_command('取消2', aliases=('取消二', ), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    await unreserve(session, 2)


@on_command('取消3', aliases=('取消三', ), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    await unreserve(session, 3)


@on_command('取消4', aliases=('取消四', ), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    await unreserve(session, 4)


@on_command('取消5', aliases=('取消五', ), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    await unreserve(session, 5)


@on_command('预约查询', aliases=('查询预约', ), permission=permission.GROUP, only_to_me=False)
async def get_reserve(session: CommandSession):
    gid = session.ctx['group_id']
    msg = '当前各王预约：'
    for i in range(1, 6):
        msg += '\n' + await see_reserve(gid, i)

    await session.finish(msg)


@on_command('挂树', aliases=('上树', ), permission=permission.GROUP, only_to_me=False)
async def up_tree(session: CommandSession):
    await reserve(session, 0)


@on_command('下树', permission=permission.GROUP, only_to_me=False)
async def down_tree(session: CommandSession):
    await unreserve(session, 0)


@on_command('查树', permission=permission.GROUP, only_to_me=False)
async def see_tree(session: CommandSession):
    gid = session.ctx['group_id']
    await session.finish(await see_reserve(gid, 0))
