import sqlite3 as sl
from datetime import datetime

ACC_DB = 'database/accounts.db'
MSB_DB = 'database/messages.db'


def see_accounts_db() -> None:
    sql_conn = sl.connect(ACC_DB)

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute("SELECT * FROM Users")

    print(sql_cursor.fetchall())


def get_acc_by(uid=None, username=None) -> tuple:
    if uid == username is None:
        raise Exception('get_acc_by() need uid or username arg.')

    sql_conn = sl.connect(ACC_DB)
    with sql_conn:
        sql_cursor = sql_conn.cursor()

        if uid is None:
            sql_cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        else:
            sql_cursor.execute("SELECT * FROM Users WHERE uid = ?", (uid,))

    return sql_cursor.fetchone()


def insert_acc(username: str, password: str) -> tuple:
    sql_conn = sl.connect(ACC_DB)

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute("INSERT INTO Users (username, password) values (?, ?)", (username, password))

    return get_acc_by(username=username)


def see_messages_db() -> None:
    sql_conn = sl.connect(MSB_DB)

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute("SELECT * FROM Messages")

    print(sql_cursor.fetchall())


def get_chat(request_uid: int, partner_uid: int) -> list:
    sql_conn = sl.connect(MSB_DB)

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute(
            "SELECT * FROM Messages " +
            "WHERE (sender_id=:rer_id AND recv_id=:ptr_id) OR (sender_id=:ptr_id AND recv_id=:rer_id)",
            {'rer_id': request_uid, 'ptr_id': partner_uid}
        )

    return sql_cursor.fetchall()


def insert_msg(sender_id: int, recv_id: int, msg_content: str) -> None:
    sql_conn = sl.connect(MSB_DB)

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute(
            "INSERT INTO Messages (sender_id, recv_id, content, timestamp) values (?, ?, ?, ?)",
            (sender_id, recv_id, msg_content, datetime.now().strftime('%m-%d-%Y, %H:%M:%S'))
        )