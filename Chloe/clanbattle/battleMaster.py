import json
from datetime import datetime, timedelta
from os import path

from .database.sqlite import DataBaseIO, getMonth


def get_config():
    config_file = path.join(path.dirname(__file__), 'config.json')
    with open(config_file, encoding='UTF-8') as f:
        config = json.load(f)
        return config


class BattleMaster(object):
    def __init__(self):
        self.databaseObj = DataBaseIO()

    @staticmethod
    def get_stage(r: int) -> int:
        if r >= 35:
            return 4
        elif r >= 11:
            return 3
        elif r >= 4:
            return 2
        else:
            return 1

    @staticmethod
    def get_boss_hp(r: int, boss: int, server: int) -> int:
        stage = BattleMaster.get_stage(r)
        config = get_config()
        return config[config["BOSS_HP"][server]][stage - 1][boss - 1]

    @staticmethod
    def get_next_boss(r: int, boss: int) -> (int, int):
        boss += 1
        if boss > 5:
            boss = 1
            r += 1
        return (r, boss)

    @staticmethod
    def get_score_rate(r: int, boss: int, server: int) -> float:
        stage = BattleMaster.get_stage(r)
        config = get_config()
        return config[config["SCORE_RATE"][server]][stage - 1][boss - 1]

    def add_clan(self, gid: int, name: str, server: int):
        self.databaseObj.addClan(gid, name, server)

    def get_clan(self, gid: int) -> (str, int) or None:
        return self.databaseObj.getClan(gid)

    def add_member(self, gid: int, uid: int, name: str):
        self.databaseObj.addMember(gid, uid, name)

    def get_member(self, gid: int, uid: int) -> str or None:
        member = self.databaseObj.getMember(gid, uid)
        if len(member) == 0:
            return None
        else:
            return member[0][1]

    # (公会名, round, boss, hp) 公会名为None表示没有公会
    def get_current_state(self, gid: int):
        clan = self.get_clan(gid)
        if clan is None:
            return (None, 1, 1, 1)

        name, server = clan

        recs = self.get_rec(gid)
        r, boss, dmg = 1, 1, 0
        if len(recs) > 0:
            r = recs[-1]['round']
            boss = recs[-1]['boss']
            for rec in recs[::-1]:
                flag, ri, bi = rec['flag'], rec['round'], rec['boss']
                if flag == 1:
                    r, boss = BattleMaster.get_next_boss(ri, bi)
                    dmg = 0
                    break

                if ri == r and bi == boss:
                    dmg += rec['dmg']
                else:
                    break

        hp = BattleMaster.get_boss_hp(r, boss, server) - dmg

        return (name, r, boss, hp)

    def get_rec(self, gid: int, uid: int = None, time: datetime = None) -> list:
        rec_cols = ['recid', 'gid', 'uid', 'time',
                    'round', 'boss', 'dmg', 'flag']

        recs = self.databaseObj.getRec(gid, uid, time)
        return [dict(zip(rec_cols, i)) for i in recs]

    def add_rec(self, gid: int, uid: int, r: int, boss: int, flag: int):
        self.databaseObj.addRec(gid, uid, r, boss, flag)

    def delete_rec(self, recid: int):
        self.databaseObj.delRec(recid)
