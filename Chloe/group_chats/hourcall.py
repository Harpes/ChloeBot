import traceback

import nonebot
import requests

from .. import send_su_message

api_url = 'https://v1.hitokoto.cn/?c=d'


async def send_groups_msg(msg: str):
    bot = nonebot.get_bot()
    try:
        group_list = await bot.get_group_list()
        for g in group_list:
            gid = g['group_id']
            await bot.send_group_msg(group_id=gid, message=msg)

    except Exception as ex:
        trace = traceback.format_exc()
        print(ex, str(trace))
        await send_su_message('hourcall 错误\n' + str(trace))

    return


# @nonebot.scheduler.scheduled_job('cron', hour='*')
# @nonebot.scheduler.scheduled_job('cron', minute='*/5')
@nonebot.scheduler.scheduled_job('cron', hour=8, minute=0, misfire_grace_time=3600)
async def _():
    resp = requests.get(api_url)
    if resp.status_code != 200:
        await send_su_message(api_url + 'fetch failed, hourcall canceled')
        return

    result = resp.json()
    hitokoto = result['hitokoto']
    await send_groups_msg(hitokoto)
