import socket
import json
from datetime import datetime

HEADER_SIZE = 1024
FORMAT = 'utf-8'

SERVER = "127.0.0.1"
PORT = int(datetime.now().strftime('%H%M0'))
ADDR = (SERVER, PORT)

SERVER_CODE = {'sign_up': '1000',
               'sign_in': '1001',
               'post_msg': '1002',
               'get_msg': '1003',
               'disconnect': '9999'}

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send_header(server_code, data):
    data_length = len(data)

    header = server_code + ',' + str(data_length)
    header += ' ' * (HEADER_SIZE - len(header))

    client.send(header.encode(FORMAT))


def post_msg(data):
    send_header(SERVER_CODE['post_msg'], data)
    client.send(data.encode(FORMAT))

    print(client.recv(HEADER_SIZE).decode(FORMAT))


def disconnect_from_server():
    send_header(SERVER_CODE['disconnect'], "")


m = {"sender_id": 1, "rcv_id": 2, "send_time": datetime.now().strftime(
    "%m/%d/%Y, %H:%M:%S"), "message_content": "Hello World"}
data_ = json.dumps(m)
post_msg(data_)
input()
disconnect_from_server()
