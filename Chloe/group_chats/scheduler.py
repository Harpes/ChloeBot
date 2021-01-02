import datetime
import json
from os import path

import nonebot
import requests

bot = nonebot.get_bot()


async def scheduler_reminder(msg: str):

    group_list = await bot.get_group_list()
    for g in group_list:
        gid = g['group_id']
        await bot.send_group_msg(group_id=gid, message=msg)


# 0800
# @nonebot.scheduler.scheduled_job('interval', seconds=10)
@nonebot.scheduler.scheduled_job('cron', hour=9, minute=0)
async def _():
    marker_path = path.join(path.dirname(__file__), 'marker.png')
    msg = f'[CQ:image,file=file:///{marker_path}]骑士君早上好，当日活动：\n'

    resp = requests.get('https://pcredivewiki.tw/static/data/event.json')
    if resp.status_code != 200:
        return

    events = json.loads(resp.text)
    event_messages = []
    time_formatter = '%Y/%m/%d %H:%M'
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

        msg_start = ''
        if start[:10] == today:
            msg_start = '(今日开始)'
        elif start[:10] == tomorrow:
            msg_start = '(明日开始)'
        elif end[:10] == today:
            msg_start = f'(今日{end_time.hour + 1}点结束)'
        elif end[:10] == tomorrow:
            msg_start = f'(明日{end_time.hour + 1}点结束)'

        event_messages.append(msg_start + name)

    event_messages.sort()
    msg += '\n'.join(event_messages)
    await scheduler_reminder(msg)
