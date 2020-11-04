import math
import re
from datetime import datetime, timedelta
from random import choices

import nonebot
from nonebot import CommandSession, MessageSegment, on_command, permission

from . import encode, get_start_of_day
from .battleMaster import BattleMaster

__plugin_name__ = 'clanbattle'

server_http_adress = 'http://localhost:80'


bot = nonebot.get_bot()
battleObj = BattleMaster()

boss_names = ['树上', '一王', '二王', '三王', '四王', '五王']
reg_nums = r'([0-9]+(\.?[0-9]+)?)([Ww万Kk千])?'


def format_num(value) -> str:
    return '{:,}'.format(value)


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
    try:
        name = session.argv[0]
    except Exception:
        name = str(gid)

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        battleObj.add_clan(gid, name, server)
    else:
        await session.finish(f'创建公会失败，当前群已有公会[{clan}]')

    clan, server = battleObj.get_clan(gid)
    if clan is None:
        await session.finish('创建公会失败')
    else:
        await session.finish('创建%s服公会[%s]成功' % (['日', '台', '国'][server], clan))


@on_command('创建日服公会', permission=permission.GROUP_OWNER, shell_like=True, only_to_me=False)
async def add_clan_jp(session: CommandSession):
    await add_clan(session, 0)


@on_command('创建台服公会', permission=permission.GROUP_OWNER, shell_like=True, only_to_me=False)
async def add_clan_cntw(session: CommandSession):
    await add_clan(session, 1)


@on_command('创建国服公会', permission=permission.GROUP_OWNER, shell_like=True, only_to_me=False)
async def add_clan_cn(session: CommandSession):
    await add_clan(session, 2)


def convertNums(value: str) -> float:
    match = re.match(reg_nums, value)
    if not match:
        return 1

    unit = {
        'W': 10000,
        'w': 10000,
        '万': 10000,
        'k': 1000,
        'K': 1000,
        '千': 1000,
    }.get(match.group(3), 1)
    return float(match.group(1)) * unit


def bc_calc_time_return(hp, dmg, remain) -> float:
    return min(20 + 90 - hp / dmg * (90 - remain), 90)


def bc_calc_hp(dmg, remain, t_return) -> int:
    return round(dmg * (20 + 90 - t_return) / (90 - remain))


@on_command('补偿刀', aliases=('补偿', '补偿刀计算', 'bc'), permission=permission.GROUP, shell_like=True, only_to_me=False)
async def _(session: CommandSession):
    gid = session.ctx['group_id']

    clan = battleObj.get_clan(gid)
    if clan is None or len(session.argv) < 1:
        return

    server = clan[1]
    clan, round_, boss, hp = battleObj.get_current_state(gid)
    dmg = battleObj.get_boss_hp(round_, boss, server)
    time_remian, time_return = 0, 0

    calc_type = 0

    for para in session.argv:
        para_name = para[0]
        if para_name not in ['h', 'd', 't', 'r']:
            return
        para_value = convertNums(para[1:])

        if para_name == 'h':
            hp = int(para_value)
        elif para_name == 'd':
            dmg = int(para_value)
        elif para_name == 't':
            time_remian = int(para_value)
            if time_remian > 90:
                time_remian = 90
        elif para_name == 'r':
            time_return = para_value
            if time_return > 90.0:
                time_return = 90.0
            calc_type = 1

    if calc_type == 0:
        # 根据剩余血量，过量伤害，余时，计算补偿刀时间
        if dmg < hp:
            await session.finish(f'伤害{format_num(dmg)}小于Boss血量{format_num(hp)}。', at_sender=True)
        time_return = bc_calc_time_return(hp, dmg, time_remian)
        msg = f'实际血量{format_num(hp)}，预计伤害{format_num(dmg)}，剩余时间{time_remian}秒。'
        msg += '\n补偿刀返还时间{:.1f}秒。'.format(time_return)
        await session.finish(msg, at_sender=True)

    elif calc_type == 1:
        # 根据伤害，余时，补偿刀时间，倒推需要的boss实际血量
        result = bc_calc_hp(dmg, time_remian, time_return)
        delta = hp - result
        msg = f'预计伤害{format_num(dmg)}，余时{time_remian}秒，补偿刀{time_return}秒'
        msg += f'\n需要Boss血量在{format_num(result)}以下。\n当前Boss{format_num(hp)}血，还需要削{format_num(delta)}血。'
        await session.finish(msg, at_sender=True)


async def get_progress_message(gid: int) -> str:
    clan, r, boss, hp = battleObj.get_current_state(gid)

    if clan is None:
        return '当前群没有创建公会'

    msg = '当前%d周目%s，剩余血量%s' % (r,
                               boss_names[boss], '{:,}'.format(hp))

    splitters = '\n----------\n'
    nums, enters = await see_enter(gid)
    if nums > 0:
        msg += splitters + f'当前{nums}人挑战中：\n' + enters

    return msg


@on_command('会战进度', aliases=('状态', '战况如何', '致远星战况如何'), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    gid = session.ctx['group_id']
    msg = await get_progress_message(gid)
    await session.finish(msg)


@on_command('查询尾刀', aliases=('尾刀统计', '尾刀查询', '查尾刀'), permission=permission.GROUP, only_to_me=False)
async def show_kill_rec(session: CommandSession):
    gid = session.ctx['group_id']

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    recs = battleObj.get_kill_rec(gid)
    if len(recs) == 0:
        await session.finish('当前尚无尾刀。')
        return

    msgs = [[] for _ in boss_names]
    for rec in recs:
        uid, dmg, boss, remark = rec['uid'], rec['dmg'], rec['boss'], rec['remark']
        user_name = await get_member_name(gid, int(uid))
        msg = f'{user_name}({int(dmg / 10000)}w)'
        if 'remain' in remark:
            msg = msg[:-1] + f" {remark['remain']}s)"
        msgs[boss].append(msg)

    msg = f'当前共有{len(recs)}尾刀。'
    for i, m in enumerate(msgs):
        if len(m) == 0:
            continue

        msg += '\n' + boss_names[i] + '：' + '、'.join(m)

    await session.finish(msg)


@on_command('昨日报告', permission=permission.GROUP, only_to_me=False)
async def show_report_yesterday(session: CommandSession):
    gid = session.ctx['group_id']

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    yesterday = get_start_of_day(datetime.now() - timedelta(days=1))
    recs = battleObj.get_rec(
        gid, uid=None, start=yesterday, end=get_start_of_day())
    if len(recs) == 0:
        await session.finish('昨日无出刀记录。')
        return

    rec = recs[0]
    begin_round, begin_boss = rec['round'], rec['boss']
    rec = recs[len(recs) - 1]
    end_round, end_boss = rec['round'], rec['boss']
    msg = f'昨日进度{begin_round}周目{boss_names[begin_boss]}~{end_round}周目{boss_names[end_boss]}。'
    msg += '\n详情：' + server_http_adress + '/' + \
        encode(gid) + '?' + yesterday.strftime('%Y%m%d')

    await session.finish(msg)


@on_command('报告', aliases=('出刀统计', '今日报告'), permission=permission.GROUP, only_to_me=False)
async def show_report(session: CommandSession):
    gid = session.ctx['group_id']

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    recs = battleObj.get_rec(gid, uid=None, start=get_start_of_day())
    if len(recs) == 0:
        await session.finish('今日尚无出刀记录。')
        return

    # 整刀数 尾刀数
    whole_nums, half_nums = 0, 0
    begin_round, begin_boss = recs[0]['round'], recs[0]['boss']
    end_round, end_boss = begin_round, begin_boss
    for rec in recs:
        flag, end_round, end_boss = rec['flag'], rec['round'], rec['boss']

        if flag == 0:
            whole_nums += 1
        elif flag == 1:
            half_nums += 1
        else:
            whole_nums += 1
            half_nums -= 1

    msg = '今日进度%s周目%s~%s周目%s，已出%s完整刀。' % (
        begin_round, boss_names[begin_boss], end_round, boss_names[end_boss], whole_nums)
    if half_nums != 0:
        msg = msg.replace("。", "，%s尾刀。" % (half_nums, ))

    msg += '\n详情：' + server_http_adress + '/' + encode(gid)

    await session.finish(msg)


def add_rec(gid: int, uid: int, r: int, boss: int, dmg: int, flag: int = 0, remark: dict = {}):
    battleObj.add_rec(gid, uid, r, boss, dmg, flag, remark)
    return battleObj.get_current_state(gid)


async def update_rec(gid: int, uid: int, dmg: int, remark: dict = {}):
    rec_type = 0
    over_kill = -1

    member_name = battleObj.get_member_name(gid, uid)
    if member_name is None:
        battleObj.add_member(gid, uid, await get_member_name(gid, uid))
        member_name = battleObj.get_member_name(gid, uid)

    msg = member_name

    _, prev_round, prev_boss, prev_hp = battleObj.get_current_state(gid)

    if dmg >= prev_hp:
        over_kill = dmg
        rec_type = 1
        dmg = prev_hp
    if dmg == -1 or dmg == prev_hp:
        rec_type = 1
        dmg = prev_hp

    member_recs = battleObj.get_rec(gid, uid, get_start_of_day())
    member_today_rec_nums, flag = 0, 0
    for rec in member_recs:
        flag = rec['flag']
        if flag in [0, 2, 3]:
            member_today_rec_nums += 1

    if member_today_rec_nums >= 3:
        await bot.send_group_msg(group_id=gid, message='你今天已经报满三刀了')
        return

    dmg_type, new_flag = '完整刀', rec_type
    if flag in [0, 2, 3]:
        dmg_type = ['完整刀', '尾刀'][rec_type]
    else:
        # flag = 1
        dmg_type = ['余刀', '余尾刀'][rec_type]
        new_flag = 2 + rec_type

    msg += '对%d周目%s造成了%s伤害' % (prev_round,
                               boss_names[prev_boss], format_num(dmg))
    msg += '(今日第%d刀，%s)。' % (member_today_rec_nums + 1, dmg_type)
    if new_flag == 1 and over_kill > 0:
        time_remain = 0
        if 'remain' in remark:
            time_remain = remark['remain']

        time_return = math.ceil(bc_calc_time_return(
            prev_hp, over_kill, time_remain))
        remark['remain'] = time_return
        msg += '\n造成过量伤害%s，余时%s秒，补偿刀返还时间%s秒。' % (
            format_num(over_kill), time_remain, time_return)

    msg += '\n----------\n'
    msg += await get_progress_message(gid)

    _, _, after_boss, _ = add_rec(
        gid, uid, prev_round, prev_boss, dmg, new_flag, remark)
    if prev_boss != after_boss:
        trees = ''
        enters = battleObj.get_enter(gid)
        for e in enters:
            if e['flag'] == 1:
                trees += str(MessageSegment.at(e['uid']))
        if len(trees) > 0:
            msg += f'\n----------\n可以下树了{trees}'

        on_reverse = call_reserve(gid, after_boss)
        if len(on_reverse) > 0:
            msg += f'\n----------\n新的{boss_names[after_boss]}已经出现{on_reverse}'

        clear_enter(gid)

    del_enter(gid, uid)

    await bot.send_group_msg(group_id=gid, message=msg)


async def handle_rec_report(msg: str, gid: int, uid: int):
    dmg = -2
    remark = {}

    pattern = [
        r'^[报報]刀 ?(\d+) ?(\d+)? ?$',
        r'^(?:\[CQ:at,qq=(\d+)\]) ?(\d+) ?(\d+)? ?$',
        r'^尾刀 ?(?:\[CQ:at,qq=(\d+)\])? ?$',
        r'^(?:\[CQ:at,qq=(\d+)\]) ?尾刀$'
    ]
    for i, pa in enumerate(pattern):
        match = re.match(pa, msg)
        if match:
            if i == 0:
                dmg = int(match.group(1))
                if match.group(2):
                    remark['remain'] = int(match.group(2))
            elif i == 1:
                remark['reporter'] = uid
                uid = match.group(1)
                dmg = int(match.group(2))
                if match.group(3):
                    remark['remain'] = int(match.group(3))
            elif i == 2 or i == 3:
                dmg = -1
                if match.group(1):
                    remark['reporter'] = uid
                    uid = match.group(1)

            break

    if dmg > -2:
        await update_rec(gid, uid, dmg, remark)


@bot.on_message('group')
async def _(context):
    message = context['raw_message']
    gid = context['group_id']
    uid = context['user_id']

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    await handle_rec_report(message, gid, uid)


@on_command('撤销', permission=permission.GROUP, only_to_me=False)
async def undo_rec(session: CommandSession):
    context = session.ctx
    gid = context['group_id']
    uid = context['user_id']
    auth = context['sender']['role']

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    recs = battleObj.get_rec(gid, uid=None, start=get_start_of_day())
    if len(recs) == 0:
        await session.finish('今日尚无出刀记录。')
        return

    last_rec = recs[-1]
    recid, last_uid, r, boss, dmg, remark = [last_rec[i]
                                             for i in ['recid', 'uid', 'round', 'boss', 'dmg', 'remark']]

    reporter = last_uid
    if remark and 'reporter' in remark:
        reporter = remark['reporter']
    if (last_uid != uid and reporter != uid) and auth == 'member':
        await session.finish('撤回别人的出刀记录需要管理权限。')
        return

    u_name = await get_member_name(gid, last_uid)

    msg = '已撤销%s对%s周目%s的%s伤害\n----------\n' % (
        u_name, r, boss_names[boss], '{:,}'.format(dmg))
    battleObj.delete_rec(gid, recid)

    msg += await get_progress_message(gid)

    await session.finish(msg)


psw = '0123456789'
psw = ''.join(choices(psw, k=4))


@on_command('清空会战记录', aliases=('清除会战记录', '重置进度', '重置会战进度'), permission=permission.GROUP_OWNER | permission.GROUP_ADMIN, only_to_me=False)
async def clear_rec(session: CommandSession):
    gid = session.ctx['group_id']

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    msg = session.get('message', prompt=f'此操作不可逆！请回复[{psw}]以重置会战进度').strip()
    if msg == psw:
        battleObj.clear_progress(gid)

        msg = await get_progress_message(gid)
        await session.finish(msg)


def add_enter(gid: int, uid: int, msg: str = ''):
    flag = 1 if msg == '挂树' else 0
    battleObj.add_enter(gid, uid, msg, flag)


async def see_enter(gid: int) -> (int, str):
    enters = battleObj.get_enter(gid)
    if len(enters) < 1:
        return (0, '')

    def sort_by_minutes(elem):
        return elem[1]

    msgs = []
    for e in enters:
        uid, time, remark = e['uid'], e['time'], e['remark']
        user_name = await get_member_name(gid, uid)
        kill_mark = '*尾刀*' if battleObj.if_kill(gid, uid) else ''
        time_passed = (datetime.now() -
                       datetime.strptime(time, '%Y/%m/%d %H:%M')).total_seconds() / 60
        msg = f'{kill_mark}({int(time_passed)}分钟前){user_name}'
        if remark:
            msg += '：' + remark
        msgs.append((msg, time_passed))

    msgs.sort(key=sort_by_minutes)
    return (len(msgs), '\n'.join([i[0] for i in msgs]))


def del_enter(gid: int, uid: int):
    battleObj.clear_enter(gid, uid)


def clear_enter(gid: int):
    battleObj.clear_enter(gid)


@on_command('申请出刀', aliases=('我进了', '我上了'), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    context = session.ctx
    gid = context['group_id']
    uid = context['user_id']

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    add_enter(gid, uid)
    await session.finish('已为你记录出刀状态', at_sender=True)


@on_command('取消出刀', aliases=('撤销出刀', ), permission=permission.GROUP, only_to_me=False)
async def _(session: CommandSession):
    context = session.ctx
    gid = context['group_id']
    uid = context['user_id']

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    del_enter(gid, uid)
    await session.finish('已为你取消出刀状态', at_sender=True)


@on_command('暂停', aliases=('zt', 'ZT'), permission=permission.GROUP, shell_like=True, only_to_me=False)
async def _(session: CommandSession):
    context = session.ctx
    gid = context['group_id']
    uid = context['user_id']
    argv = session.argv

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    if len(argv) == 0:
        msg = await get_progress_message(gid)
        await session.finish(msg)
        return

    add_enter(gid, uid, ' '.join(argv))
    await session.finish('已为你记录出刀状态。', at_sender=True)


@on_command('挂树', aliases=('上树', '掛樹'), permission=permission.GROUP, only_to_me=False)
async def up_tree(session: CommandSession):
    context = session.ctx
    gid = context['group_id']
    uid = context['user_id']

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    add_enter(gid, uid, '挂树')
    await session.finish('成功上树。', at_sender=True)


def add_reserve(gid: int, uid: int, boss: int) -> str:
    reservations = battleObj.get_reservation(gid, boss)
    existed = False
    for reserva in reservations:
        if reserva[0] == uid:
            existed = True
            break

    if existed:
        return f'{str(MessageSegment.at(uid))} 你已预约过{boss_names[boss]}，请勿重复预约'

    battleObj.add_reservation(gid, uid, boss)
    return f'成功预约{boss_names[boss]}，当前Boss预约人数：{len(reservations) + 1}'


def cancel_reserve(gid: int, uid: int, boss: int) -> str:
    reservations = battleObj.get_reservation(gid, boss)
    existed = False
    for reserva in reservations:
        if reserva[0] == uid:
            existed = True
            break

    if existed:
        battleObj.clear_reservation(gid, boss, uid)
        return f'已为你取消预约{boss_names[boss]}'

    return f'你尚未预约{boss_names[boss]}'


async def see_reserve(gid: int) -> str:
    reservations = battleObj.get_reservation(gid)
    if len(reservations) < 1:
        return '当前没有预约。'

    users = [[] for _ in boss_names]
    for reserva in reservations:
        uid, boss = reserva
        user_name = await get_member_name(gid, uid)
        users[boss].append(user_name)

    msg = '当前预约情况：\n'
    for b, u in enumerate(users):
        if len(u) > 0:
            msg += f"{boss_names[b]}{len(u)}人：{'、'.join(u)}\n"

    return msg[:-1]


def call_reserve(gid: int, boss: int) -> str:
    reservations = battleObj.get_reservation(gid, boss)
    battleObj.clear_reservation(gid, boss)

    msg = ''
    for res in reservations:
        msg += str(MessageSegment.at(res[0]))

    return msg


async def reserve(session: CommandSession, boss: int):
    context = session.ctx
    gid = context['group_id']
    uid = context['user_id']

    clan, _ = battleObj.get_clan(gid)
    if clan is None:
        return

    msg = add_reserve(gid, uid, boss)
    await session.finish(msg)


async def unreserve(session: CommandSession, boss: int):
    context = session.ctx
    gid = context['group_id']
    uid = context['user_id']

    clan, _ = battleObj.get_clan(gid)
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


@on_command('预约查询', aliases=('查询预约', '查预约'), permission=permission.GROUP, only_to_me=False)
async def get_reserve(session: CommandSession):
    gid = session.ctx['group_id']
    msg = await see_reserve(gid)

    await session.finish(msg)
