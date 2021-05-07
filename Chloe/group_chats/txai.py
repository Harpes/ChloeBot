import random
import string
import time
from hashlib import md5
from urllib import parse

import requests

from ..config import get_configuration_key

# https://ai.qq.com/doc/nlpchat.shtml
appid = get_configuration_key('txai_appid')
appkey = get_configuration_key('txai_appkey')


def get_nonce_str():
    nonce = ''.join(random.sample(string.ascii_letters + string.digits, 10))
    return nonce


def get_time_stamp():
    return int(time.time())


def get_nlp_chats(question: str, session: str) -> str:
    if len(appkey) < 1:
        return ''

    args = [
        ('app_id', appid),
        ('nonce_str',  get_nonce_str()),
        ('question', question),
        ('session', session),
        ('time_stamp', get_time_stamp()),
    ]
    args.sort()
    sign = parse.urlencode(args)
    sign += f'&app_key={appkey}'
    sign = md5(sign.encode(encoding='utf8')).hexdigest().upper()

    args.append(('sign', sign))
    querys = parse.urlencode(args)
    resp = requests.get(
        f'https://api.ai.qq.com/fcgi-bin/nlp/nlp_textchat?{querys}')

    res = resp.json()
    if res['ret'] == 0:
        return res['data']['answer']

    return ''
