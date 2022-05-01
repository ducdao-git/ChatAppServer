import sqlite3 as sl


def get_acc_by(uid=None, username=None):
    if uid == username is None:
        raise Exception('get_acc_by() need uid or username arg.')

    sql_conn = sl.connect('database/accounts.db')
    with sql_conn:
        sql_cursor = sql_conn.cursor()

        if uid is None:
            sql_cursor.execute("SELECT * FROM Users WHERE username = ?", (username,))
        else:
            sql_cursor.execute("SELECT * FROM Users WHERE uid = ?", (uid,))

        # entry = sql_cursor.fetchone()
        # print(entry)
        # print(type(entry))

    return sql_cursor.fetchone()


def insert_acc(username, password):
    sql_conn = sl.connect('database/accounts.db')

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute("INSERT INTO Users (username, password) values (?, ?)", (username, password))

    return get_acc_by(username=username)


def see_account_db():
    sql_conn = sl.connect('database/accounts.db')

    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute("SELECT * FROM Users")

    print(sql_cursor.fetchall())
