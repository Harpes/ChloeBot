import datetime
import json
import re

import requests
from nonebot import CommandSession, on_command


@on_command('Tnews', aliases=('台服新闻', '台服公告'))
async def Tnews(session: CommandSession):
    url = 'http://www.princessconnect.so-net.tw/news'

    resp = requests.get(url)
    if resp.status_code != 200:
        await session.finish(f'查询失败 {resp.status_code}')
        return
    data = resp.text

    # 标题
    pattern_title = '<a href="/news/newsDetail/.*?">(.*?)</a>'  # 标题
    title = re.findall(pattern_title, data)
    # 链接
    pattern_link = '<a href="/news/(.*?)\\"'
    link0 = re.findall(pattern_link, data)
    link = [f'{url}/{i}' for i in link0]
    # 发布时间
    pattern_time = '(.*?)<span class=".*?">'
    time0 = re.findall(pattern_time, data)
    time = [i.strip() for i in time0]

    msgs = []
    for i in range(len(title)):
        msgs.append(f'{time[i]} {title[i]}\n{link[i]}')
    await session.send(message='\n'.join(msgs))


@on_command('Tevents', aliases=('台服活动',))
async def Tevents(session: CommandSession):
    url = 'https://pcredivewiki.tw/static/data/event.json'

    resp = requests.get(url)
    if resp.status_code != 200:
        await session.finish(f'查询失败 {resp.status_code}')
    data = json.loads(resp.text, encoding='utf8')

    n = datetime.datetime.now()
    msg0 = '已查询到以下活动：'
    for i in data:
        t = datetime.datetime.strptime(i['end_time'], '%Y/%m/%d %H:%M')
        if t > n:
            msg = (
                f"\n- {i['campaign_name'].strip()}\n{i['start_time'][5:]}-{i['end_time'][5:]}")
            msg0 += msg
    await session.send(message=msg0)


@on_command('anime_search', aliases=('以图搜番', '这是什么番', '搜番', '什么番', '番剧查询', '这是什么动漫', '动漫查询', '搜动漫', '什么动漫'), only_to_me=False)
async def anime_search(session: CommandSession):
    msg = session.current_arg.strip()
    if not msg:
        msg = session.get('message', prompt='准备完成，请发送图片')
    p = '\\[CQ\\:image\\,file\\=.*?\\,url\\=(.*?)\\]'
    img = re.findall(p, msg)
    if img:
        url = f'https://trace.moe/api/search?url={img[0]}'
        r = requests.get(url)
        if r.status_code == 200:
            data = json.loads(r.text, encoding='utf8')
            d = {}
            for i in range(len(data['docs'])):
                if data['docs'][i]['title_chinese'] in d.keys():
                    d[data['docs'][i]['title_chinese']
                      ][0] += data['docs'][i]['similarity']
                else:
                    m = data['docs'][i]['at']/60
                    s = data['docs'][i]['at'] % 60
                    if data['docs'][i]['episode'] == '':
                        n = 1
                    else:
                        n = data['docs'][i]['episode']
                    d[data['docs'][i]['title_chinese']] = [
                        data['docs'][i]['similarity'], f'第{n}集', f'{int(m)}分{int(s)}秒处']
            result = sorted(d.items(), key=lambda x: x[1], reverse=True)
            t = 0

            msg = ''
            if session.ctx['message_type'] == 'group':
                msg = '[CQ:at,qq={}] '.format(str(session.ctx['user_id']))

            msg0 = f'为骑士君{msg}按相似度找到以下{len(d)}个动漫：'
            for i in result:
                t += 1
                msg = (
                    f'\n({t})\n相似度：{i[1][0]}\n动漫名：《{i[0]}》\n时间点：{i[1][1]} {i[1][2]}')
                msg0 += msg
            await session.send(msg0)
        else:
            await session.send('在下太忙啦，过会再来问吧')
