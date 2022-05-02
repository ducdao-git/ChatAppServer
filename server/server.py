import json
import socket
import sys
import threading

import database.db_logic as db

HEADER_SIZE = 1024
FORMAT = 'utf-8'

SERVER = socket.gethostbyname(socket.gethostname())
# PORT = int(datetime.now().strftime('%H%M0'))
PORT = 5050
ADDR = (SERVER, PORT)


def sign_up_handle(json_str_data):
    data = json.loads(json_str_data)  # username, password
    acc_info = db.get_acc_by(username=data['username'])

    if acc_info is not None:
        # print(f"uid: -1 -- taken username")
        return -1
    else:
        acc_info = db.insert_acc(data['username'], data['password'])
        return acc_info[0]  # acc uid


def log_in_handle(json_str_data):
    data = json.loads(json_str_data)  # username, password
    acc_info = db.get_acc_by(username=data['username'])

    if acc_info is None:
        return -1  # no acc with username
    elif data['password'] != acc_info[2]:
        return -2  # wrong password
    else:
        return acc_info[0]  # acc uid


# def post_message_handle(json_str_data):
#     data = json.loads(json_str_data)
#
#     sender_info = db.get_acc_by(uid=int(data['sender_id']))
#     if sender_info is None:
#         return -1  # no acc with uid
#     elif data['sender_pw'] != sender_info[2]:
#         return -2  # wrong password
#
#     recv_info = db.get_acc_by(username=str(data['recv_username']))
#     if recv_info is None:
#         return -3  # no recv with username
#
#     db.insert_msg(int(sender_info[0]), int(recv_info[0]), str(data['msg_content']))
#
#     return 0

def get_messages_handle(json_str_data):
    data = json.loads(json_str_data)

    sender_info = db.get_acc_by(uid=int(data['sender_id']))
    if sender_info is None:
        return -1  # no acc with uid
    elif data['sender_pw'] != sender_info[2]:
        return -2  # wrong password

    partner_info = db.get_acc_by(username=str(data['partner_username']))
    if partner_info is None:
        return -3  # no acc with username

    chat = db.get_chat(sender_info[0], partner_info[0])
    for i in range(len(chat)):
        msg = list(chat[i])

        if msg[1] == sender_info[0]:
            msg[1] = sender_info[1]
            msg[2] = partner_info[1]
        else:
            msg[1] = partner_info[1]
            msg[2] = sender_info[1]

        chat[i] = msg

    print(f'\n\nget_msg_handle: {chat}\n\n')
    return chat


SERVER_CODE = {'sign_up': '1000',
               'log_in': '1001',
               'post_msg': '1002',
               'get_msg': '1003',
               'disconnect': '9999'}


def handle_client(client_conn, client_addr):
    print(f"[NEW CONNECTION] {client_addr} connected.")

    while True:
        header = client_conn.recv(HEADER_SIZE).decode(FORMAT)
        header = header.strip()
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

                case 1001:
                    uid = log_in_handle(data)
                    client_conn.send(str(uid).encode(FORMAT))

                # case 1002:
                #     resp_code = post_message_handle(data)
                #     client_conn.send(f"{resp_code}".encode(FORMAT))

                case 1003:
                    resp = get_messages_handle(data)
                    if isinstance(resp, int):
                        client_conn.send(f"{resp}".encode(FORMAT))  # send error-code
                    else:
                        chat = json.dumps(resp)
                        chat_size_str = str(sys.getsizeof(chat))
                        chat_size_send_str = \
                            chat_size_str + ' ' * (HEADER_SIZE * 2 - len(chat_size_str))

                        client_conn.send(chat_size_send_str.encode(FORMAT))  # send chat size
                        client_conn.send(chat.encode(FORMAT))  # send chat

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
