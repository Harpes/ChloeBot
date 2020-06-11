import os
import sqlite3
from datetime import datetime, timedelta, timezone

DB_folder = 'clanbattle'
if not os.path.exists(DB_folder):
    os.mkdir(DB_folder)


def getMonth(time: datetime) -> str:
    day = time - timedelta(hours=5)
    if day.day < 20:
        day -= timedelta(days=day.day)

    return day.strftime("%Y%m")


class DataBaseIO(object):
    def connect(self, gid: int):
        db_path = os.path.join(DB_folder, '%s.db' % (gid, ))
        return sqlite3.connect(db_path)

    def createTable(self, gid: int, table_name: str, cols: list) -> sqlite3.Connection:
        conn = self.connect(gid)
        create_sql = 'CREATE TABLE IF NOT EXISTS %s(%s)' % (
            table_name, ','.join(cols))
        conn.execute(create_sql)
        return conn

    def _createClan(self, gid: int) -> sqlite3.Connection:
        return self.createTable(gid, 'clan', [
            'gid INT PRIMARY KEY NOT NULL', 'name TEXT NOT NULL', 'server INT NOT NULL'])

    def addClan(self, gid: int, name: str, server: int):
        conn = self._createClan(gid)

        insert_sql = 'INSERT INTO clan VALUES (%s, "%s", %s)' % (
            gid, name, server)
        conn.execute(insert_sql)

        conn.commit()
        conn.close()

    def getClan(self, gid: int) -> list:
        conn = self._createClan(gid)
        cur = conn.cursor()

        select_sql = 'SELECT name, server FROM clan WHERE gid = %s' % (gid, )
        cur.execute(select_sql)
        result = cur.fetchone()

        conn.commit()
        conn.close()

        return result

    def _createMember(self, gid: int) -> (sqlite3.Connection, str):
        month = getMonth(datetime.now())
        return (self.createTable(gid, 'member' + month, ['gid INT NOT NULL', 'uid INT NOT NULL',
                                                         'name TEXT NOT NULL', 'PRIMARY KEY (gid, uid)']), month)

    def addMember(self, gid: int, uid: int, name: str):
        conn, month = self._createMember(gid)

        insert_sql = 'INSERT INTO member%s VALUES (%s, %s, "%s")' % (
            month, gid, uid, name)
        conn.execute(insert_sql)

        conn.commit()
        conn.close()

    def getMember(self, gid: int, uid: int = None):
        conn, month = self._createMember(gid)
        cur = conn.cursor()

        select_sql = 'SELECT uid, name FROM member%s WHERE gid = %s' % (
            month, gid)
        if not uid is None:
            select_sql += ' AND uid = %s' % (uid, )
        cur.execute(select_sql)
        result = cur.fetchall()

        conn.commit()
        conn.close()

        return result

    def _createRecs(self, gid: int) -> (sqlite3.Connection, str):
        month = getMonth(datetime.now())
        return (self.createTable(gid, 'rec' + month, ['recid INTEGER PRIMARY KEY AUTOINCREMENT',
                                                      'gid INT NOT NULL', 'uid INT NOT NULL',
                                                      'time TIMESTAMP NOT NULL', 'round INT NOT NULL',
                                                      'boss INT NOT NULL', 'dmg INT NOT NULL',
                                                      'flag INT NOT NULL']), month)

    # flag: 0:正常刀 1:尾刀 2:余刀 3:余尾刀
    def addRec(self, gid: int, uid: int, r: int, b: int, dmg: int, flag: int):
        conn, month = self._createRecs(gid)

        insert_sql = 'INSERT INTO rec%s VALUES (NULL, %s, %s, "%s", %s, %s, %s, %s)' % (
            month, gid, uid, datetime.now().strftime('%Y/%m/%d %H:%M'), r, b, dmg, flag)
        conn.execute(insert_sql)

        conn.commit()
        conn.close()

    def getRec(self, gid: int, uid: int = None, start: datetime = None, end: datetime = None) -> list:
        conn, month = self._createRecs(gid)
        cur = conn.cursor()

        select_sql = 'SELECT * FROM rec%s WHERE gid = %s' % (month, gid)
        if not uid is None:
            select_sql += ' AND uid = %s' % (uid, )
        if not start is None:
            select_sql += ' AND time > "%s"' % (
                start.strftime('%Y/%m/%d %H:%M'), )
        if not end is None:
            select_sql += ' AND time < "%s"' % (
                end.strftime('%Y/%m/%d %H:%M'), )

        cur.execute(select_sql)
        result = cur.fetchall()

        conn.commit()
        conn.close()

        return result

    def delRec(self, gid: int, recid: int):
        conn, month = self._createRecs(gid)

        delete_sql = 'DELETE FROM rec%s WHERE recid = %s' % (month, recid)
        conn.execute(delete_sql)

        conn.commit()
        conn.close()
