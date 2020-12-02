from nonebot import CommandSession, on_command, permission


@on_command('test', permission=permission.SUPERUSER)
async def test_function(session: CommandSession):
    a = await session.bot.get_status()
    await session.finish(message=str(session.ctx) + '\n' + str(a))
