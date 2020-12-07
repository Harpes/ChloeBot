import nonebot
from quart import jsonify, request
from quart_compress import Compress

from . import decode, encode
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


@bot.server_app.route('/mems')
async def get_mems():
    gid = request.args.get('g')
    result = {}

    try:
        gid = decode(gid)
        mems = battleObj.list_member(gid)
        for uid, name in mems:
            print(uid, name)
            result[encode(uid)] = name

        return jsonify(result)
    except Exception:
        return jsonify({})
