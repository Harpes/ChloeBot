import base64
from io import BytesIO
from os import path

import nonebot
from nonebot.command import CommandSession
from PIL import Image, ImageDraw, ImageFont

MODULES_ON = {
    'clanbattle',
    'group_chats',
    'manager',
    'steam_notification',
}

fontMSYH = ImageFont.truetype('msyhl.ttc', 14)


def init(config) -> nonebot.NoneBot:
    nonebot.init(config)
    bot = nonebot.get_bot()

    for module_name in MODULES_ON:
        module_path = path.join(path.dirname(__file__), module_name)
        nonebot.load_plugins(module_path, f'Chloe.{module_name}')

    return bot


async def send_su_message(msg: str):
    bot = nonebot.get_bot()
    await bot.send_private_msg(user_id=bot.config.SUPERUSERS[0], message=msg)


# From https://github.com/AkiraXie/HoshinoBot
def get_text_size(text: str, font: ImageFont.ImageFont, padding=(20, 20, 20, 20), spacing: int = 5) -> tuple:
    '''
    返回文本转图片的图片大小

    *`text`：用来转图的文本
    *`font`：一个`ImageFont`实例
    *`padding`：一个四元`int`元组，分别是左、右、上、下的留白大小
    *`spacing`: 文本行间距
    '''
    with Image.new('RGBA', (1, 1), (255, 255, 255, 255)) as base:
        dr = ImageDraw.ImageDraw(base)
    ret = dr.textsize(text, font=font, spacing=spacing)
    return ret[0] + padding[0] + padding[1], ret[1] + padding[2] + padding[3]


def text2pic(text: str, font: ImageFont.ImageFont = fontMSYH, padding=(20, 20, 20, 20), spacing: int = 5) -> Image.Image:
    '''
    返回一个文本转化后的`Image`实例

    *`text`：用来转图的文本
    *`font`：一个`ImageFont`实例
    *`padding`：一个四元`int`元组，分别是左、右、上、下的留白大小
    *`spacing`: 文本行间距
    '''
    size = get_text_size(text, font, padding, spacing)
    base = Image.new('RGBA', size, (255, 255, 255, 255))
    dr = ImageDraw.ImageDraw(base)
    dr.text((padding[0], padding[2]), text, font=font,
            fill='#000000', spacing=spacing)
    return base


def pic2b64(pic: Image.Image) -> str:
    buf = BytesIO()
    pic.save(buf, format='PNG')
    base64_str = base64.b64encode(buf.getvalue()).decode()
    return 'base64://' + base64_str


def pic2msg(pic: Image.Image) -> str:
    # TODO: find out why MessageSegment.image doesn't work
    # return MessageSegment.image(pic2b64(pic))
    return f'[CQ:image,file={pic2b64(pic)}]'


def get_username(session: CommandSession) -> str:
    sender = session.ctx['sender']
    card = sender.get('card', '')
    nickname = sender.get('nickname', '')

    res = ''
    if len(card) > 0 and 'CQ' not in card:
        res = card
    elif len(nickname) > 0 and 'CQ' not in nickname:
        res = nickname

    return res


def get_msg_header(session: CommandSession) -> str:
    message_type = session.ctx['message_type']
    if message_type == 'private':
        return ''

    return f'>{get_username(session)}\n'


async def session_send_message(session: CommandSession, message: str, commandName: str):
    try:
        await session.send(message, ignore_failure=False)
    except Exception:
        pic = text2pic(message)
        try:
            await session.send(pic2msg(pic))
        except Exception:
            gid = session.ctx['group_id']
            await send_su_message(f'群{gid}发送消息失败：{commandName}\n{message}')
