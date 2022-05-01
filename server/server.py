import json
import socket
import threading
import sqlite3 as sl
from datetime import datetime

HEADER_SIZE = 1024
FORMAT = 'utf-8'

SERVER = socket.gethostbyname(socket.gethostname())
PORT = int(datetime.now().strftime('%H%M0'))
ADDR = (SERVER, PORT)


def post_message_handle(json_str_data):
    data = json.loads(json_str_data)
    print(f'{type(data)}: {data}')


def sign_up_handle(json_str_data):
    data = json.loads(json_str_data)  # username, password

    sql_conn = sl.connect('database/accounts.db')
    with sql_conn:
        sql_cursor = sql_conn.cursor()
        sql_cursor.execute("SELECT * FROM Users WHERE username = ?", (data['username'],))

        if sql_cursor.fetchone() is not None:
            print(f"uid: -1 -- taken username")
            return -1  # the username is taken
        else:
            sql_cursor.execute("INSERT INTO Users (username, password) values (?, ?)",
                               (data['username'], data['password']))

        sql_cursor.execute("SELECT uid FROM Users WHERE username = ?", (data['username'],))
        user_id = sql_cursor.fetchone()[0]

    print(f"uid: {user_id}")
    return user_id


server_code_mapping = {
    1000: 'sign_up',
    1001: 'sign_in',
    1002: 'post_message',
    1003: 'get_message',
    9999: 'disconnect',
}


def handle_client(client_conn, client_addr):
    print(f"[NEW CONNECTION] {client_addr} connected.")

    while True:
        header = client_conn.recv(HEADER_SIZE).decode(FORMAT)
        header = header.rstrip()
        # print(f"header: {header}")

        server_code, data_length = header.split(',')
        # print(f"server_code, data_length: {server_code}, {data_length}")

        if server_code.isdigit() and data_length.isdigit():
            server_code = int(server_code)
            if server_code == 9999:  # close client connection
                break

            data_length = int(data_length)
            data = client_conn.recv(data_length).decode(FORMAT)  # get a string (can be json-string)

            match server_code:
                case 1000:
                    uid = sign_up_handle(data)
                    client_conn.send(str(uid).encode(FORMAT))

                case 1002:
                    post_message_handle(data)
                    client_conn.send("Data received".encode(FORMAT))

    client_conn.close()


def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    server.listen()
    print(f"[LISTENING] Server is listening on {ADDR}")

    while True:
        client_conn, client_addr = server.accept()

        thread = threading.Thread(target=handle_client, args=(client_conn, client_addr))
        thread.start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")


start_server()
