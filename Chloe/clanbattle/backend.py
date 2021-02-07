import nonebot
from quart import jsonify, request, websocket
from quart_compress import Compress

from . import decode, encode, get_clan
from .battleMaster import BattleMaster

bot = nonebot.get_bot()
battleObj = BattleMaster()

Compress(bot.server_app)


@bot.server_app.route('/recs')
async def get_recs():
    gid = request.args.get('g')
    uid = request.args.get('u')

    try:
        gid = decode(gid)
        if uid is not None:
            uid = decode(uid)

        recs = battleObj.get_rec(gid, uid)
        result = [{
            'uid': encode(rec['uid']),
            'time': rec['time'],
            'round': rec['round'],
            'boss': rec['boss'],
            'dmg': rec['dmg'],
            'flag': rec['flag'],
            'score': rec['score'],
            # 'remark': rec['remark']
        }for rec in recs]
        return jsonify(result)
    except Exception:
        return jsonify([])


@bot.server_app.route('/mem')
async def get_mem():
    gid = request.args.get('g')
    uid = request.args.get('u')

    try:
        gid = decode(gid)
        uid = decode(uid)

        return battleObj.get_member_name(gid, uid)
    except Exception:
        return ''


@bot.server_app.route('/mems')
async def get_mems():
    gid = request.args.get('g')

    try:
        gid = decode(gid)
        clan, _ = get_clan(gid)

        result = {'name': clan or ''}
        mems = battleObj.list_member(gid)
        for uid, name in mems:
            result[encode(uid)] = name

        return jsonify(result)
    except Exception:
        return jsonify({})


@bot.server_app.websocket('/ws')
async def websockets():
    while True:
        data = await websocket.receive()
        await websocket.send(f"echo {data}")
