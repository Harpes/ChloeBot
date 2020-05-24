import datetime
import json

import nonebot
from aiohttp import ClientSession
from nonebot import CommandSession, on_command

bot = nonebot.get_bot()


async def get_bytes(url, headers=None):
    async with ClientSession() as asyncsession:
        async with asyncsession.get(url, headers=headers) as response:
            b = await response.read()
    return b


async def scheduler_reminder(msg: str):
    group_list = await bot.get_group_list()
    for group in group_list:
        try:
            await bot.send_group_msg(group_id=group['group_id'], message=msg)
        except:
            pass


# 0800
@nonebot.scheduler.scheduled_job('cron', hour=8, minute=0)
async def _():
    msg = '骑士君早上好，当日活动：\n'

    header = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }
    url = 'https://pcredivewiki.tw/static/data/event.json'
    time_formatter = '%Y/%m/%d %H:%M'

    data = await get_bytes(url, headers=header)

    events = json.loads(data.decode())
    event_messages = []
    now = datetime.datetime.now()
    today = now.strftime(time_formatter)[:10]
    tomorrow = (now + datetime.timedelta(days=1)).strftime(time_formatter)[:10]

    for ev in events:
        start, end, name, predict = ev['start_time'], ev['end_time'], ev['campaign_name'], ev['isPredict']
        if predict == '1':
            continue

        start_time = datetime.datetime.strptime(start, time_formatter)
        end_time = datetime.datetime.strptime(end, time_formatter)
        if end_time < now or start_time > (now + datetime.timedelta(days=2)):
            continue

        msg_start = ""
        if start[:10] == today:
            msg_start = "(今日开始)"
        elif start[:10] == tomorrow:
            msg_start = "(明日开始)"
        elif end[:10] == today:
            msg_start = f"(今日{end_time.hour + 1}点结束)"
        elif end[:10] == tomorrow:
            msg_start = f"(明日{end_time.hour + 1}点结束)"

        event_messages.append(msg_start + name)

    event_messages.sort()
    msg += '\n'.join(event_messages)
    await scheduler_reminder(msg)

# 2330
@nonebot.scheduler.scheduled_job('cron', hour=23, minute=30)
async def _():
    msg = '现在23:30，骑士君该睡觉了！'
    await scheduler_reminder(msg)
