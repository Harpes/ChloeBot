import json
from os import path
from xml.etree import ElementTree

import nonebot
import requests
from nonebot import CommandSession, on_command, permission, scheduler

steam_api_key = 'XXX'

# PERSONASTATE = {0: 'Offline', 1: 'Online', 2: 'Busy', 3: 'Away',
#                 4: 'Snooze', 5: 'looking to trade', 6: 'looking to play'}
PERSONASTATE = {0: '离线', 1: '在线', 2: '忙碌', 3: '离开',
                4: '打盹', 5: '寻找交易', 6: '找游戏'}

player_states = {}


config_file = path.join(path.dirname(__file__), 'config.json')
if not path.exists(config_file):
    json.dump({}, open(config_file, 'w'))


def load_config(key: str, default_value=''):
    return json.load(open(config_file, 'r')).get(key, default_value)


def save_config(key: str, value):
    config = json.load(open(config_file, 'r'))
    config[key] = value
    json.dump(config, open(config_file, 'w'))


def get_steam_user_id(id: str) -> str:
    if id.startswith('76561198') and len(id) == 17:
        return id
    else:
        resp = requests.get(f'https://steamcommunity.com/id/{id}?xml=1')
        xml = ElementTree.XML(resp.content)
        return xml.findtext('steamID64')


def get_account_status(ids):
    if isinstance(ids, str):
        ids = (get_steam_user_id(ids),)
    else:
        ids = map(lambda x: get_steam_user_id(x), set(ids))

    ids = ','.join(ids)
    resp = requests.get(
        f'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={steam_api_key}&steamids={ids}')
    return resp.json()['response']['players']


def update_player_state(state: dict):
    steamid = state['steamid']
    personaname = state['personaname']
    personastate = state['personastate']
    gameextrainfo = state.get('gameextrainfo', '')
    lastlogoff = state['lastlogoff']

    player_states[steamid] = [personaname,
                              personastate, gameextrainfo, lastlogoff]


def get_player_state(steamid: str):
    steamid = get_steam_user_id(steamid)
    return player_states.get(steamid, None)


@on_command('添加steam订阅', permission=permission.SUPERUSER, shell_like=True, only_to_me=False)
async def _(session: CommandSession):
    argv = session.argv
    if len(argv) < 1:
        await session.finish('请输入要订阅的steamID，以空格隔开')

    subscribes = load_config('subscribes', [])
    accounts = get_account_status(argv)
    if len(accounts) < 1:
        await session.finish('查询失败！')

    msgs = []
    for account in accounts:
        update_player_state(account)

        steamid = account['steamid']
        personaname = account['personaname']
        personastate = account['personastate']

        if steamid not in subscribes:
            subscribes.append(steamid)
            msgs.append(f'{personaname} 当前{PERSONASTATE[personastate]}')
        else:
            msgs.append(f'{personaname} 已在订阅中')

    if len(msgs) > 0:
        save_config('subscribes', subscribes)
        await session.finish('\n'.join(msgs))
    else:
        await session.finish('找不到steam账号，订阅失败')


@on_command('steam订阅列表', aliases=('steam', 'steam订阅'), permission=permission.SUPERUSER, only_to_me=False)
async def _(session: CommandSession):
    subscribes = load_config('subscribes', [])
    status = get_account_status(subscribes)
    msgs = []
    for sta in status:
        personaname = sta['personaname']
        personastate = sta['personastate']
        gameextrainfo = sta.get('gameextrainfo', '')

        msg = personaname
        if gameextrainfo:
            msg += ' 正在游玩 ' + gameextrainfo
        else:
            msg += ' 当前 ' + PERSONASTATE[personastate]
        msgs.append(msg)

    if len(msgs) > 0:
        await session.finish('\n'.join(msgs))


@scheduler.scheduled_job('cron', minute='*/2')
async def _():
    notificate_group_id = ()
    if len(notificate_group_id) < 1:
        return

    subscribes = load_config('subscribes', [])
    account_status = get_account_status(subscribes)
    msgs = []
    for acc in account_status:
        steamid = acc['steamid']
        personaname = acc['personaname']
        # personastate = acc['personastate']
        gameextrainfo = acc.get('gameextrainfo', '')

        old_state = get_player_state(steamid)
        if old_state:
            pre_personaname, pre_personastate, pre_gameextrainfo, _ = old_state
            if gameextrainfo != pre_gameextrainfo:
                if gameextrainfo:
                    msgs.append(f'{personaname} 开始游玩 「{gameextrainfo}」')
                else:
                    msgs.append(f'{personaname} 不再游玩 「{pre_gameextrainfo}」')

        update_player_state(acc)

    if len(msgs) > 0:
        bot = nonebot.get_bot()
        msg = '\n'.join(msgs)
        for gid in notificate_group_id:
            await bot.send_group_msg(group_id=gid, message=msg)
