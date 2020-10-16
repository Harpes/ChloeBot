import json
import re
from io import BytesIO
from os import path

import requests
import zhconv
from nonebot import CommandSession, on_command, permission
from PIL import Image

icon_url = 'https://redive.estertion.win/icon/unit/'
res_path = 'res'
icon_path = path.join(res_path, 'unit')
CHARA = {}
NAME2ID = {}


def normname(name: str) -> str:
    name = name.lower().replace('（', '(').replace('）', ')')
    name = zhconv.convert(name, 'zh-hans')
    return name


def load_Chara() -> dict:
    global CHARA, NAME2ID
    CHARA = json.load(
        open(path.join('config', 'chara.json'), 'r', encoding='utf8'))

    for k, l in CHARA.items():
        for n in l:
            if n not in NAME2ID:
                NAME2ID[normname(n)] = k
            else:
                print(f'出现重名{n}于id{k}与id{NAME2ID[n]}')


load_Chara()


@on_command('重载花名册', permission=permission.SUPERUSER)
async def _(session: CommandSession):
    load_Chara()
    await session.finish('重载完成')

gadget_star = Image.open(path.join(res_path, 'gadget', 'star.png'))
gadget_pink = Image.open(path.join(res_path, 'gadget', 'star_pink.png'))
gadget_equip = Image.open(path.join(res_path, 'gadget', 'equip.png'))
# gadget_star_dis = Image.open(
#     path.join(res_path, 'gadget', 'start_disabled.png'))
chara_unknown = Image.open(path.join(res_path, 'unit', 'icon_unit_100031.png'))


def get_chara_id(name: str) -> int:
    return NAME2ID.get(normname(name), 1000)


def get_chara_name(id_: int) -> str:
    return CHARA.get(id_, [None, '未知角色'])[1]


def get_chara_icon(id_: int, star: int = 3, download: bool = True) -> Image:
    stage = [3, 1, 1, 3, 3, 3, 6][star]

    img_path = path.join(icon_path, f'icon_unit_{id_}{stage}1.png')
    if path.exists(img_path):
        return Image.open(img_path)
    elif download:
        download_unit_icon(id_)
        return get_chara_icon(id_, star, False)
    else:
        print(f'{id_} {star}x 图片文件未找到')
        return chara_unknown


def save_img(link: str, des: str):
    destination = path.join(icon_path, des)
    if path.exists(destination):
        return

    try:
        resp = requests.get(icon_url + link, stream=True, timeout=3)
    except Exception:
        return

    if resp.status_code == 200 and re.search(r'image', resp.headers['content-type'], re.I):
        img = Image.open(BytesIO(resp.content))
        img.save(destination)
        print('下载到新文件', des)


def gen_icon_filename(id_, pre, end):
    return f'{pre}{id_:0>4d}{end}'


def download_unit_icon(id_: int):
    for star in [1, 3, 6]:
        link = gen_icon_filename(id_, '', f'{star}1.webp')
        des = gen_icon_filename(id_, 'icon_unit_', f'{star}1.png')
        save_img(link, des)


def gen_chara_avatar(id_: int, star: int = 3, equip: bool = False) -> Image:
    icon = get_chara_icon(id_, star)
    size = icon.size[0]

    le = size // 6
    star_lap = round(le * 0.15)
    margin_x = (size - 6 * le) // 2
    margin_y = round(size * 0.05)

    if star == 6:
        star_icon = gadget_pink.resize((le, le))
        x = margin_x
        y = size - le - margin_y
        icon.paste(star_icon, (x, y, x + le, y + le), star_icon)
    else:
        star_icon = gadget_star.resize((le, le))
        for i in range(star):
            x = i * (le - star_lap) + margin_x
            y = size - le - margin_y
            icon.paste(star_icon, (x, y, x + le, y + le), star_icon)

    if equip:
        le = round(le * 1.5)
        equip_icon = gadget_equip.resize((le, le))
        icon.paste(equip_icon, (margin_x, margin_x,
                                margin_x + le, margin_x + le), equip_icon)

    return icon
