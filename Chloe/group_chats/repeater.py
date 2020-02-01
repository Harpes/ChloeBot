from random import randint

import nonebot

bot = nonebot.get_bot()


@bot.on_message('group')
async def _(context):
    message = context['raw_message']
    group_id = context['group_id']

    if randint(0, 100) < 4:
        await bot.send_group_msg(group_id=group_id, message=message)
