import json
from datetime import datetime, timedelta

from flask import Flask, abort, jsonify, render_template, request
from flask_compress import Compress
from gevent import pywsgi

from Chloe.clanbattle import decode, encode, get_start_of_day
from Chloe.clanbattle.battleMaster import BattleMaster

app = Flask(__name__, static_folder='./web', template_folder='./web')
Compress(app)

battleObj = BattleMaster()


@app.route('/')
def root_error():
    return 'Parameters error'


@app.route('/<string:group>', methods=['GET'])
def rec_main(group):
    gid = decode(group)

    name, _, _, _ = battleObj.get_current_state(gid)
    if name is None:
        abort(404)

    title = f'公会 {name}'

    return render_template('index.html', title=title, render_type='recs')


@app.route('/static/<path:file_path>', methods=['GET'])
def rec_file(file_path):
    return app.send_static_file(file_path)


@app.route('/recs/<string:group>', methods=['GET'])
def get_recs(group):
    try:
        gid = decode(group)

        date = request.args.get('date')
        start, end = None, None
        if date is None:
            start = get_start_of_day()
        else:
            start = get_start_of_day(datetime.strptime(
                date, '%Y%m%d'))+timedelta(days=1)
            end = start + timedelta(days=1)

        uid = request.args.get('uid')
        if not uid is None:
            uid = decode(uid)

        recs = battleObj.get_rec(gid, uid, start, end)
    except:
        abort(404)

    result = []
    for rec in recs:
        result.append({
            'uid': encode(rec['uid']),
            'time': rec['time'],
            'round': rec['round'],
            'boss': rec['boss'],
            'dmg': rec['dmg'],
            'flag': rec['flag'],
            'score': rec['score']
        })

    return jsonify(result)


@app.route('/members/<string:group>', methods=['GET'])
def get_members(group):
    result = {}
    try:
        gid = decode(group)
        mems = battleObj.list_member(gid)
        for m in mems:
            uid, name = m
            result[encode(uid)] = name
    except:
        abort(404)

    return jsonify(result)


if __name__ == '__main__':
    # app.run(debug=True, port=80)
    server = pywsgi.WSGIServer(('0.0.0.0', 80), app)
    server.serve_forever()
