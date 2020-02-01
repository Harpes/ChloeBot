from datetime import datetime

import nonebot

bot = nonebot.get_bot()


async def scheduler_reminder(msg: str):
    group_list = await bot.get_group_list()
    try:
        for group in group_list:
            await bot.send_group_msg(group_id=group, message=msg)
    except:
        pass


# 1450
@nonebot.scheduler.scheduled_job('cron', hour=14, minute=50, misfire_grace_time=30)
async def _():
    msg = '背刺Time背刺Time背刺Time背刺Time背刺Time!!!\n大家记得背刺群主'
    await scheduler_reminder(msg)

# 1456
@nonebot.scheduler.scheduled_job('cron', hour=14, minute=56, misfire_grace_time=30)
async def _():
    msg = str(datetime.now())
    await scheduler_reminder(msg)

# 0800
@nonebot.scheduler.scheduled_job('cron', hour=8, misfire_grace_time=30)
async def _():
    msg = '起床啦！！！'
    await scheduler_reminder(msg)

# 2300
@nonebot.scheduler.scheduled_job('cron', hour=23, misfire_grace_time=30)
async def _():
    msg = '现在23点，骑士君该睡觉了！'
    await scheduler_reminder(msg)
