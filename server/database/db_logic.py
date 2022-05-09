import sqlite3 as sl
from datetime import datetime

ACC_DB = 'database/accounts.db'
MSB_DB = 'database/messages.db'


def see_accounts_db() -> None:
    """
    Print the Users database (for dev use only)
    """
    sql_conn = sl.connect(ACC_DB)

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute("SELECT * FROM Users")

    print(sql_cursor.fetchall())


def get_acc_by(uid=None, username=None) -> tuple:
    """
    Get an account info by either user ID or username. User ID or username must be
    provided when called. If both provided, will search by user ID.

    :param uid: int repr user ID
    :param username: str repr account's username

    :return: (int, str, str) repr (uid, username, password) about an account
    """
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
    """
    Insert an entry (repr acc) to the Users database

    :param username: str repr the username of the account
    :param password: str repr the password of the account

    :return: (int, str, str) repr (uid, username, password) about the inserted account
    """
    sql_conn = sl.connect(ACC_DB)

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute("INSERT INTO Users (username, password) values (?, ?)", (username, password))

    return get_acc_by(username=username)


def see_messages_db() -> None:
    """
    Print the Messages database (for dev use only)
    """
    sql_conn = sl.connect(MSB_DB)

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute("SELECT * FROM Messages")

    print(sql_cursor.fetchall())


def get_chat(request_uid: int, partner_uid: int, fetch_size=50) -> list:
    """
    Get all message sent or received by two user IDs.

    :param request_uid: int repr user ID of account request the get chat
    :param partner_uid: int repr user ID of account that request_uid have chat with
    :param fetch_size: int repr number of messages will be fetched in one call

    :return: list of all messages sent and received between two user ID.
        Each message has the form (mid, sender_id, recv_id, message_content)
    """
    sql_conn = sl.connect(MSB_DB)

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute(
            "SELECT * FROM Messages " +
            "WHERE (sender_id=:rer_id AND recv_id=:ptr_id) OR (sender_id=:ptr_id AND recv_id=:rer_id)",
            {'rer_id': request_uid, 'ptr_id': partner_uid}
        )

    return sql_cursor.fetchmany(fetch_size)


def insert_msg(sender_id: int, recv_id: int, msg_content: str) -> None:
    """
    Insert a message to the database

    :param sender_id: int repr user ID of the sender account
    :param recv_id: int repr user ID of the recipient account
    :param msg_content: str repr the content of a message
    """
    sql_conn = sl.connect(MSB_DB)

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute(
            "INSERT INTO Messages (sender_id, recv_id, content, timestamp) values (?, ?, ?, ?)",
            (sender_id, recv_id, msg_content, datetime.now().strftime('%m-%d-%Y, %H:%M:%S'))
        )
