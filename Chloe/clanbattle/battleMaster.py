import json
from datetime import datetime
from os import path

from . import add_clan as add_clan_def
from . import get_clan as get_clan_def
from . import get_start_of_day
from .database.sqlite import DataBaseIO


def get_config():
    config_file = path.join('config', 'clanbattle.json')
    with open(config_file, encoding='UTF-8') as f:
        config = json.load(f)
        return config


class BattleMaster(object):
    def __init__(self):
        self.databaseObj = DataBaseIO()

    def get_stage(self, r: int) -> int:
        if r >= 35:
            return 4
        elif r >= 11:
            return 3
        elif r >= 4:
            return 2
        else:
            return 1

    def get_boss_hp(self, r: int, boss: int, server: int) -> int:
        stage = self.get_stage(r)
        config = get_config()
        return config[config["BOSS_HP"][server]][stage - 1][boss - 1]

    def get_next_boss(self, r: int, boss: int) -> (int, int):
        boss += 1
        if boss > 5:
            boss = 1
            r += 1

        return (r, boss)

    def get_score_rate(self, r: int, boss: int, server: int) -> float:
        stage = self.get_stage(r)
        config = get_config()
        return config[config["SCORE_RATE"][server]][stage - 1][boss - 1]

    def add_clan(self, gid: int, name: str, server: int):
        add_clan_def(gid, name, server)

    def get_clan(self, gid: int) -> (str, int):
        return get_clan_def(gid)

    def add_member(self, gid: int, uid: int, name: str):
        self.databaseObj.add_member(gid, uid, name)

    def del_member(self, gid: int, uid: int):
        self.databaseObj.del_member(gid, uid)

    def get_member_name(self, gid: int, uid: int) -> str or None:
        member = self.databaseObj.get_member(gid, uid)
        if len(member) == 0:
            return None
        else:
            return member[0][1]

    def list_member(self, gid: int) -> list:
        return self.databaseObj.get_member(gid)

    # (公会名, round, boss, hp) 公会名为None表示没有公会
    def get_current_state(self, gid: int) -> (str, int, int, int):
        name, server = self.get_clan(gid)
        if name is None:
            return (None, -1, -1, -1)

        recs = self.get_rec(gid)
        r, boss, dmg = 1, 1, 0
        if len(recs) > 0:
            r = recs[-1]['round']
            boss = recs[-1]['boss']
            for rec in recs[::-1]:
                flag, ri, bi = rec['flag'], rec['round'], rec['boss']
                if ri == r and bi == boss:
                    if flag == 1 or flag == 3:
                        r, boss = self.get_next_boss(ri, bi)
                        dmg = 0
                        break
                    else:
                        dmg += rec['dmg']
                else:
                    break

        hp = self.get_boss_hp(r, boss, server) - dmg

        return (name, r, boss, hp)

    def clear_progress(self, gid: int):
        self.databaseObj.clear_rec(gid)
        self.databaseObj.clear_enter(gid)

    # flag: 0:正常刀 1:尾刀 2:余刀 3:余尾刀
    def add_rec(self, gid: int, uid: int, r: int, boss: int, dmg: int, flag: int, remark: dict = {}):
        self.databaseObj.add_rec(
            gid, uid, r, boss, dmg, flag, json.dumps(remark))

    def get_rec(self, gid: int, uid: int = None, start: datetime = None, end: datetime = None) -> list:
        cols = ['recid', 'uid', 'time', 'round',
                'boss', 'dmg', 'flag', 'remark']
        recs = self.databaseObj.get_rec(gid, uid, start, end)
        results = [dict(zip(cols, i)) for i in recs]
        _, server = self.get_clan(gid)
        for rec in results:
            r, b, d, remark = rec['round'], rec['boss'], rec['dmg'], rec['remark']
            rate = self.get_score_rate(r, b, server)
            rec['score'] = int(d * rate)
            if remark:
                rec['remark'] = json.loads(remark)

        return results

    def delete_rec(self, gid: int, recid: int):
        self.databaseObj.del_rec(gid, recid)

    # flag: 0:正常 1:挂树
    def add_enter(self, gid: int, uid: int, remark: str, flag: int = 0):
        self.databaseObj.unvalid_enter(gid, uid)
        self.databaseObj.add_enter(gid, uid, remark, flag)

    def get_enter(self, gid: int) -> list:
        cols = ['recid', 'uid', 'time', 'remark', 'flag', 'valid']
        enters = self.databaseObj.get_enter(gid, start=get_start_of_day())
        results = [dict(zip(cols, i)) for i in enters]
        return results

    def clear_enter(self, gid: int, uid: int = None):
        self.databaseObj.unvalid_enter(gid, uid)

    def add_reservation(self, gid: int, uid: int, boss: int):
        self.databaseObj.add_reservation(gid, uid, boss)

    def get_reservation(self, gid: int, boss: int = None) -> list:
        return self.databaseObj.get_reservation(gid, boss)

    def clear_reservation(self, gid: int, boss: int, uid: int = None):
        self.databaseObj.clear_reservation(gid, boss, uid)

    # 获取当前的尾刀
    def get_kill_rec(self, gid: int) -> list:
        recs = self.get_rec(gid, start=get_start_of_day())
        user_kills = {}
        for rec in recs:
            uid, flag = rec['uid'], rec['flag']
            if flag == 1:
                user_kills[uid] = rec
            elif uid in user_kills:
                del user_kills[uid]

        result = [rec for rec in user_kills.values()]
        return result

    # 判断当前玩家是否持有尾刀
    def if_kill(self, gid: int, uid: int) -> bool:
        recs = self.get_rec(gid, uid, get_start_of_day())
        result = False
        for rec in recs:
            if rec['flag'] == 1:
                result = True
            else:
                result = False

        return result
