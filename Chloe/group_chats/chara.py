import json
import re
import traceback
from io import BytesIO
from os import path

import requests
import zhconv
from nonebot import CommandSession, on_command, permission, scheduler
from PIL import Image

from .. import pic2msg, send_su_message
from .fetch_pcr_nicknames import get_pcr_nickname_data

icon_url = 'https://redive.estertion.win/icon/unit/'
res_path = 'res'
icon_path = path.join(res_path, 'unit')
chara_path = path.join('config', 'chara.json')
CHARA = {}
NAME2ID = {}


def normname(name: str) -> str:
    name = name.lower().replace('（', '(').replace('）', ')')
    name = zhconv.convert(name, 'zh-hans')
    return name


def load_Chara():
    global CHARA, NAME2ID
    CHARA = json.load(open(chara_path, 'r', encoding='utf8'))
    NAME2ID = {}

    err_msg = ''
    for id_, name_list in CHARA.items():
        for n in name_list:
            name = normname(n)
            if name not in NAME2ID:
                NAME2ID[name] = int(id_)
            else:
                msg = f'出现重名{name}于id{id_}与id{NAME2ID[name]}'
                print(msg)
                err_msg += msg + '\n'

    return err_msg[:-1]


load_Chara()


@on_command('更新花名册', permission=permission.SUPERUSER)
async def _(session: CommandSession):
    global CHARA

    err_msg = await update_chara()
    if err_msg:
        await send_su_message(err_msg)

    new_icons = []
    for chara_id in CHARA.keys():
        if chara_id == '1000':
            continue

        icons = download_unit_icon(int(chara_id), False)
        new_icons.extend(icons)

    if len(new_icons) > 0:
        ile = 60
        pic = Image.new("RGB", (ile * len(new_icons), ile), 'white')
        for i, p in enumerate(new_icons):
            pic.paste(p.resize((ile, ile)), (i * ile, 0))

        await send_su_message(f'获取到新头像{pic2msg(pic)}')


# @scheduler.scheduled_job('interval', seconds=10)
@scheduler.scheduled_job('cron', hour=4)
async def update_chara():
    new_chara = {}
    old_chara = json.load(open(chara_path, 'r', encoding='utf8'))
    delta_chara = {}

    try:
        coming_chara = get_pcr_nickname_data()
        for chara_id, coming_names in coming_chara.items():
            if(int(chara_id) > 1900):
                continue

            old_names = old_chara.get(str(chara_id), [])
            delta_names = []
            for name in coming_names:
                t_name = normname(name)
                if len(t_name) > 0 and t_name not in old_names and t_name not in NAME2ID:
                    delta_names.append(t_name)

                new_chara[str(chara_id)] = old_names + delta_names
                if len(delta_names) > 0:
                    delta_chara[chara_id] = delta_names

        if delta_chara:
            json.dump(new_chara, open(chara_path, 'w',
                                      encoding='utf8'), ensure_ascii=False)
            msg = '获取到新的角色名称'
            for chara_id, d_names in delta_chara.items():
                msg += f'\n「{str(chara_id)}」{"、".join(d_names)}'
            await send_su_message(msg)

    except Exception as ex:
        trace = traceback.format_exc()
        print(ex)
        await send_su_message(f'更新角色名单错误\n{trace}')
        json.dump(old_chara, open(chara_path, 'w',
                                  encoding='utf8'), ensure_ascii=False)

        return

    return load_Chara()


gadget_star = Image.open(path.join(res_path, 'gadget', 'star.png'))
gadget_pink = Image.open(path.join(res_path, 'gadget', 'star_pink.png'))
gadget_equip = Image.open(path.join(res_path, 'gadget', 'equip.png'))
# gadget_star_dis = Image.open(
#     path.join(res_path, 'gadget', 'start_disabled.png'))
chara_unknown = Image.open(path.join(res_path, 'unit', 'icon_unit_100031.png'))


def get_chara_id(name: str) -> int:
    return NAME2ID.get(normname(name), 1000)


def get_chara_name(id_: int) -> str:
    return CHARA.get(str(id_), ['未知角色', ])[0]


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
        # print(des, 'existed, skiped.')
        return

    try:
        resp = requests.get(icon_url + link, stream=True, timeout=3)
    except Exception:
        return

    if resp.status_code == 200 and re.search(r'image', resp.headers['content-type'], re.I):
        img = Image.open(BytesIO(resp.content))
        img.save(destination)
        # print('下载到新文件', des)
        return img


def gen_icon_filename(id_, pre, end):
    return f'{pre}{id_:0>4d}{end}'


def download_unit_icon(id_: int, download_six: bool = True):
    stars = [1, 3]
    if download_six:
        stars.append(6)

    new_icons = []
    for star in stars:
        link = gen_icon_filename(id_, '', f'{star}1.webp')
        des = gen_icon_filename(id_, 'icon_unit_', f'{star}1.png')
        res = save_img(link, des)
        if res:
            new_icons.append(res)

    return new_icons


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
