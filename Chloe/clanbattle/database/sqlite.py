import os
import sqlite3
from datetime import datetime

from .. import DB_folder, get_month


class DataBaseIO(object):
    def __connect(self, gid: int) -> sqlite3.Connection:
        db_path = os.path.join(DB_folder, '%s.db' % (gid, ))
        return sqlite3.connect(db_path)

    def __create_table(self, gid: int, table_name: str, cols: list) -> (sqlite3.Connection, str):
        conn = self.__connect(gid)
        table_name = '%s_%s' % (table_name, get_month())
        create_sql = 'CREATE TABLE IF NOT EXISTS %s(%s)' % (
            table_name, ','.join(cols))
        conn.execute(create_sql)
        return (conn, table_name)

    def _create_member(self, gid: int) -> (sqlite3.Connection, str):
        columns = [
            'uid INT PRIMARY KEY',
            'name TEXT NOT NULL',
        ]
        return self.__create_table(gid, 'member', columns)

    def add_member(self, gid: int, uid: int, name: str):
        conn, table_name = self._create_member(gid)

        insert_sql = 'INSERT INTO %s VALUES (%s, "%s")' % (
            table_name, uid, name)
        conn.execute(insert_sql)
        conn.commit()
        conn.close()

    def get_member(self, gid: int, uid: int = None) -> list:
        conn, table_name = self._create_member(gid)
        cur = conn.cursor()

        select_sql = 'SELECT uid, name FROM %s' % (table_name, )
        if uid is not None:
            select_sql += ' WHERE uid = %s' % (uid, )
        cur.execute(select_sql)
        result = cur.fetchall()
        conn.close()

        return result

    def del_member(self, gid: int, uid: int):
        conn, table_name = self._create_member(gid)

        delete_sql = 'DELETE FROM %s WHERE uid = %s' % (table_name, uid)
        conn.execute(delete_sql)
        conn.commit()
        conn.close()

    def _create_rec(self, gid: int) -> (sqlite3.Connection, str):
        columns = [
            'recid INTEGER PRIMARY KEY AUTOINCREMENT',
            'uid INT NOT NULL',
            'time TIMESTAMP NOT NULL', 'round INT NOT NULL',
            'boss INT NOT NULL', 'dmg INT NOT NULL',
            'flag INT NOT NULL', 'remark TEXT NOT NULL'
        ]
        return self.__create_table(gid, 'recs', columns)

    # flag: 0:正常刀 1:尾刀 2:余刀 3:余尾刀
    def add_rec(self, gid: int, uid: int, r: int, b: int, dmg: int, flag: int, remark: str):
        conn, table_name = self._create_rec(gid)

        insert_sql = '''INSERT INTO %s VALUES (NULL, %s, '%s', %s, %s, %s, %s, '%s')''' % (
            table_name, uid, datetime.now().strftime('%Y/%m/%d %H:%M'), r, b, dmg, flag, remark)
        conn.execute(insert_sql)
        conn.commit()
        conn.close()

    def get_rec(self, gid: int, uid: int = None, start: datetime = None, end: datetime = None) -> list:
        conn, table_name = self._create_rec(gid)
        cur = conn.cursor()

        select_sql = 'SELECT * FROM %s WHERE 0 = 0' % (table_name, )
        if uid is not None:
            select_sql += ' AND uid = %s' % (uid, )
        if start is not None:
            select_sql += ' AND time > "%s"' % (
                start.strftime('%Y/%m/%d %H:%M'), )
        if end is not None:
            select_sql += ' AND time < "%s"' % (
                end.strftime('%Y/%m/%d %H:%M'), )

        cur.execute(select_sql)
        result = cur.fetchall()
        conn.close()

        return result

    def del_rec(self, gid: int, recid: int):
        conn, table_name = self._create_rec(gid)

        delete_sql = 'DELETE FROM %s WHERE recid = %s' % (table_name, recid)
        conn.execute(delete_sql)
        conn.commit()
        conn.close()

    def clear_rec(self, gid: int):
        conn, table_name = self._create_rec(gid)

        drop_sql = 'DROP TABLE ' + table_name
        conn.execute(drop_sql)
        conn.commit()
        conn.close()

    def _create_enter(self, gid: int) -> (sqlite3.Connection, str):
        columns = [
            'recid INTEGER PRIMARY KEY AUTOINCREMENT',
            'uid INT NOT NULL',
            'time TIMESTAMP NOT NULL',
            'remark TEXT NOT NULL',
            'flag INT NOT NULL',
            'valid INT NOT NULL'
        ]
        return self.__create_table(gid, 'enter', columns)

    def add_enter(self, gid: int, uid: int, remark: str, flag: int):
        conn, table_name = self._create_enter(gid)

        insert_sql = 'INSERT INTO %s VALUES (NULL, %s, "%s", "%s", %s, 1)' % (
            table_name, uid, datetime.now().strftime('%Y/%m/%d %H:%M'), remark, flag)
        conn.execute(insert_sql)
        conn.commit()
        conn.close()

    def get_enter(self, gid: int, uid: int = None, start: datetime = None, end: datetime = None, flag: int = None) -> list:
        conn, table_name = self._create_enter(gid)
        cur = conn.cursor()

        select_sql = 'SELECT * FROM %s WHERE valid = 1' % (table_name, )
        if uid is not None:
            select_sql += ' AND uid = %s' % (uid, )
        if start is not None:
            select_sql += ' AND time > "%s"' % (
                start.strftime('%Y/%m/%d %H:%M'), )
        if end is not None:
            select_sql += ' AND time < "%s"' % (
                end.strftime('%Y/%m/%d %H:%M'), )
        if flag is not None:
            select_sql += ' AND flag = %s' % (flag, )

        cur.execute(select_sql)
        result = cur.fetchall()
        conn.close()

        return result

    def unvalid_enter(self, gid: int, uid: int = None):
        conn, table_name = self._create_enter(gid)

        update_sql = 'UPDATE %s SET valid = 0 WHERE valid = 1' % (table_name, )
        if uid is not None:
            update_sql += ' AND uid = %s' % (uid, )

        conn.execute(update_sql)
        conn.commit()
        conn.close()

    def clear_enter(self, gid: int):
        conn, table_name = self._create_enter(gid)

        drop_sql = 'DROP TABLE ' + table_name
        conn.execute(drop_sql)
        conn.commit()
        conn.close()

    def _create_reservation(self, gid: int) -> (sqlite3.Connection, str):
        columns = [
            'recid INTEGER PRIMARY KEY AUTOINCREMENT',
            'uid INT NOT NULL',
            'boss INT NOT NULL',
            'time TIMESTAMP NOT NULL',
            'remark TEXT NOT NULL',
            'valid INT NOT NULL'
        ]
        return self.__create_table(gid, 'reservation', columns)

    def add_reservation(self, gid: int, uid: int, boss: int):
        conn, table_name = self._create_reservation(gid)

        insert_sql = 'INSERT INTO %s VALUES (NULL, %s, %s, "%s", "", 1)' % (
            table_name, uid, boss,  datetime.now().strftime('%Y/%m/%d %H:%M'))
        conn.execute(insert_sql)
        conn.commit()
        conn.close()

    def get_reservation(self, gid: int, boss: int = None) -> list:
        conn, table_name = self._create_reservation(gid)
        cur = conn.cursor()

        select_sql = 'SELECT uid, boss FROM %s WHERE valid = 1' % (
            table_name, )
        if boss is not None:
            select_sql += ' AND boss = %s' % (boss, )

        cur.execute(select_sql)
        results = cur.fetchall()
        conn.close()

        return results

    def clear_reservation(self, gid: int, boss: int, uid: int = None):
        conn, table_name = self._create_reservation(gid)

        update_sql = 'UPDATE %s SET valid = 0 WHERE valid = 1 AND boss = %s' % (
            table_name, boss)
        if uid is not None:
            update_sql += ' AND uid = %s' % (uid, )
        conn.execute(update_sql)
        conn.commit()
        conn.close()
