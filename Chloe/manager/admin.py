from nonebot import CommandSession, on_command, permission


@on_command('查询群信息', permission=permission.SUPERUSER)
async def _(session: CommandSession):
    group_list = await session.bot.get_group_list()
    msg = '一共有{}个群：'.format(len(group_list))
    for group in group_list:
        msg += '\n-----------------\n'+'群名称:' + \
            group['group_name'] + '\n' + '群号:' + str(group['group_id'])
    await session.send(msg)
