import socket
import json
from datetime import datetime

HEADER_SIZE = 1024
FORMAT = 'utf-8'

SERVER = socket.gethostbyname(socket.gethostname())
PORT = int(datetime.now().strftime('%H%M0'))
ADDR = (SERVER, PORT)

SERVER_CODE = {'sign_up': '1000',
               'sign_in': '1001',
               'post_msg': '1002',
               'get_msg': '1003',
               'disconnect': '9999'}

print(ADDR)
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send_header(server_code, data_len):
    header = server_code + ',' + str(data_len)
    header += ' ' * (HEADER_SIZE - len(header))

    client.send(header.encode(FORMAT))


def post_msg(data):
    send_header(SERVER_CODE['post_msg'], len(data))
    client.send(data.encode(FORMAT))

    print(client.recv(HEADER_SIZE).decode(FORMAT))


def sign_up(username, password):
    signup_info = {'username': username, 'password': password}
    signup_info = json.dumps(signup_info)

    send_header(SERVER_CODE['sign_up'], len(signup_info))
    client.send(signup_info.encode(FORMAT))

    # server respond with uid, and -1 mean the username taken
    print(client.recv(HEADER_SIZE).decode(FORMAT))


def disconnect_from_server():
    send_header(SERVER_CODE['disconnect'], 0)


# # -------------------------------- post msg test --------------------------------
m = {"sender_id": 1, "rcv_id": 2, "send_time": datetime.now().strftime(
    "%m/%d/%Y, %H:%M:%S"), "message_content": "Hello World"}
data_ = json.dumps(m)
post_msg(data_)
# input()

# -------------------------------- signup test --------------------------------
# sign_up('dtuser4', 'Jk3WnSu2')

# -------------------------------- disconnect --------------------------------
disconnect_from_server()
