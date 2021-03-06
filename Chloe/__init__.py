import base64
from io import BytesIO
from os import path

import nonebot
from nonebot import MessageSegment
from PIL import Image, ImageDraw, ImageFont

MODULES_ON = {
    'clanbattle',
    'group_chats',
    'manager',
    # 'arcaea',
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
    return MessageSegment.image(pic2b64(pic))
