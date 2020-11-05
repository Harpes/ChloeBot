from nonebot import CommandSession, on_command, permission


@on_command('test', permission=permission.SUPERUSER)
async def test_function(session: CommandSession):
    print(session.ctx)
    await session.finish(message=str(session.ctx))
