import json
from datetime import datetime, timedelta
from os import path

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
        self.databaseObj.addClan(gid, name, server)

    def get_clan(self, gid: int) -> (str, int) or None:
        return self.databaseObj.getClan(gid)

    def add_member(self, gid: int, uid: int, name: str):
        self.databaseObj.addMember(gid, uid, name)

    def get_member_name(self, gid: int, uid: int) -> str or None:
        member = self.databaseObj.getMember(gid, uid)
        if len(member) == 0:
            return None
        else:
            return member[0][1]

    def list_member(self, gid: int) -> list:
        return self.databaseObj.getMember(gid)

    # (公会名, round, boss, hp) 公会名为None表示没有公会
    def get_current_state(self, gid: int) -> (str, int, int, int):
        clan = self.get_clan(gid)
        if clan is None:
            return (None, -1, -1, -1)

        name, server = clan

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

    def get_rec(self, gid: int, uid: int = None, start: datetime = None, end: datetime = None) -> list:
        rec_cols = ['recid', 'gid', 'uid', 'time',
                    'round', 'boss', 'dmg', 'flag']
        recs = self.databaseObj.getRec(gid, uid, start, end)
        results = [dict(zip(rec_cols, i)) for i in recs]
        _, server = self.get_clan(gid)
        for rec in results:
            r, b, d = rec['round'], rec['boss'], rec['dmg']
            rate = self.get_score_rate(r, b, server)
            rec['score'] = int(d * rate)

        return results

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

    def add_rec(self, gid: int, uid: int, r: int, boss: int, dmg: int, flag: int):
        self.databaseObj.addRec(gid, uid, r, boss, dmg, flag)

    def delete_rec(self, gid: int, recid: int):
        self.databaseObj.delRec(gid, recid)

    def clear_rec(self, gid: int):
        recs = self.get_rec(gid)
        for r in recs:
            self.delete_rec(gid, r['recid'])
