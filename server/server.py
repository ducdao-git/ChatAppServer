import json
import socket
import sys
import threading
from datetime import datetime

import database.db_logic as db

HEADER_SIZE = 1024
FORMAT = 'utf-8'

# SERVER = socket.gethostbyname(socket.gethostname())
SERVER = '127.0.0.1'
# PORT = int(datetime.now().strftime('%H%M0'))
PORT = 5050
ADDR = (SERVER, PORT)

SERVER_CODE = {'sign_up': '1000',
               'log_in': '1001',
               'post_msg': '1002',
               'get_msg': '1003',
               'disconnect': '9999'}


def sign_up_handle(json_str_data):
    """
    Handle sign up request. Extract and pass data to database helper
    function to create a new account.

    :param json_str_data: string repr valid json obj with (username, password)

    :return:
         -1: error - username is taken
         uid: positive int repr user ID if successful add a new account to database
    """
    data = json.loads(json_str_data)  # username, password
    acc_info = db.get_acc_by(username=data['username'])

    if acc_info is not None:
        # print(f"uid: -1 -- taken username")
        return -1
    else:
        acc_info = db.insert_acc(data['username'], data['password'])
        return acc_info[0]  # acc uid


def log_in_handle(json_str_data):
    """
    Handle log in request. Extract and pass data to database helper
    function to check client credential.

    :param json_str_data: string repr valid json obj with (username, password)

    :return:
        -1: error - no account with username
        -2: error - wrong password for account with this username
        uid: positive int repr user ID if the credential is correct for the user in database
    """
    data = json.loads(json_str_data)  # username, password
    acc_info = db.get_acc_by(username=data['username'])

    if acc_info is None:
        return -1  # no acc with username
    elif data['password'] != acc_info[2]:
        return -2  # wrong password
    else:
        return acc_info[0]  # acc uid


def post_message_handle(json_str_data):
    """
    Handle the post a message request. Extract and pass data to database helper
    function to check if the client is authorized and can post a msg. If user
    is authorized, the function also user database helper to store the message in
    database

    :param json_str_data: string repr valid json obj with (sender_id, sender_pw,
           recv_username, msg_content)

    :return:
        -1: error - no account with sender user ID
        -2: error - sender user has wrong password
        -3: error - no account with recv username
         0: the message is posted and stored in the database
    """
    data = json.loads(json_str_data)

    sender_info = db.get_acc_by(uid=int(data['sender_id']))
    if sender_info is None:
        return -1  # no acc with uid
    elif data['sender_pw'] != sender_info[2]:
        return -2  # wrong password

    recv_info = db.get_acc_by(username=str(data['recv_username']))
    if recv_info is None:
        return -3  # no recv with username

    db.insert_msg(int(sender_info[0]), int(recv_info[0]), str(data['msg_content']))

    return 0


def get_messages_handle(json_str_data):
    """
    Handle the get messages request. Extract and pass data to database helper
    function to check if the client is authorized and can have msgs content

    :param json_str_data: string repr valid json obj with (sender_id, sender_pw,
           partner_username)

    :return:
        -1: error - no account with sender user ID
        -2: error - sender user has wrong password
        -3: error - no account with partner username
        jsonObj: repr a list of chat msgs between 2 users. Each msg in form:
            {msg_id, sender_id, recipient_id, msg_content}
    """
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

    # print(f'\n\nget_msg_handle: {chat}\n\n')
    return chat


def handle_client(client_conn, client_addr):
    """
    Handle each client connection, will direct the connection to correct handle func
    depend on what server_code the client sent. The function also responsible for
    sending respond of the server handle function back to the client.

    The list of server_code can be seen next to each case below or at the top of this
    python file for reference.

    :param client_conn: the actual client connection
    :param client_addr: (ip_addr, port_number) repr client's address
    :return: None
    """
    print(f"[NEW CONNECTION] {client_addr} connected.")

    while True:
        header = client_conn.recv(HEADER_SIZE).decode(FORMAT)
        header = header.strip()
        server_code, data_length = header.split(',')

        if server_code.isdigit() and data_length.isdigit():
            server_code = int(server_code)
            if server_code == 9999:  # server code for close client connection
                client_conn.close()
                print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 2}\n")
                return

            data_length = int(data_length)
            data = client_conn.recv(data_length).decode(FORMAT)  # get a string (can be json-string)

            match server_code:
                case 1000:  # server_code for sign-up
                    uid = sign_up_handle(data)
                    client_conn.send(str(uid).encode(FORMAT))

                case 1001:  # server_code for log-up
                    uid = log_in_handle(data)
                    client_conn.send(str(uid).encode(FORMAT))

                case 1002:  # server_code for post message
                    resp_code = post_message_handle(data)  # no error (0), error (-1 -> -3)
                    client_conn.send(f"{resp_code}".encode(FORMAT))

                case 1003:  # server_code for get messages
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


def start_server():
    """
    Start the server, listen to all connection, start new thread for each connection
    so no connection need to wait upon each other. The function also make sure all the
    connections are closed properly.

    The use of threading and server listening is learned from this website:
    https://www.techwithtim.net/tutorials/socket-programming/

    :return: None
    """
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(ADDR)

    try:
        server.listen()
        print(f"[LISTENING] Server is listening on {ADDR}")

        while True:
            client_conn, client_addr = server.accept()

            thread = threading.Thread(target=handle_client, args=(client_conn, client_addr))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1} \n")

    except KeyboardInterrupt:
        return

    finally:
        server.close()


start_server()
