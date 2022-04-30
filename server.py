import json
import socket
import threading
from datetime import datetime

HEADER_SIZE = 1024
FORMAT = 'utf-8'

SERVER = socket.gethostbyname(socket.gethostname())
PORT = int(datetime.now().strftime('%H%M0'))
ADDR = (SERVER, PORT)

DISCONNECT = 9999


def post_message_handle(json_str_data):
    data = json.loads(json_str_data)
    print(f'inside post_message_handle: {data}')
    print(type(data))


def sign_up_handle(json_str_data):
    pass


server_code_mapping = {
    1000: 'sign_up',
    1001: 'sign_in',
    1002: post_message_handle,
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

            server_code_mapping[server_code](data)

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

