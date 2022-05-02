import socket
import json

HEADER_SIZE = 1024
FORMAT = 'utf-8'

SERVER = socket.gethostbyname(socket.gethostname())
# PORT = int(datetime.now().strftime('%H%M0'))
PORT = 5051
ADDR = (SERVER, PORT)

SERVER_CODE = {'sign_up': '1000',
               'log_in': '1001',
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


def sign_up(username, password):
    signup_info = {'username': username, 'password': password}
    signup_info = json.dumps(signup_info)

    send_header(SERVER_CODE['sign_up'], len(signup_info))
    client.send(signup_info.encode(FORMAT))

    # server respond with uid, or -1 mean the username taken
    server_resp = client.recv(10).decode(FORMAT)
    if server_resp == '-1':
        return '-1'
    else:
        return AuthorizedUser(server_resp, username, password)


def log_in(username, password):
    login_info = {'username': username, 'password': password}
    login_info = json.dumps(login_info)

    send_header(SERVER_CODE['log_in'], len(login_info))
    client.send(login_info.encode(FORMAT))

    # server respond with uid, no acc (-1), or wrong pw (-2)
    server_resp = client.recv(10).decode(FORMAT)
    if server_resp in ['-1', '-2']:
        return server_resp
    else:
        return AuthorizedUser(server_resp, username, password)


def disconnect_from_server():
    send_header(SERVER_CODE['disconnect'], 0)


class AuthorizedUser:
    """class represent logged-in user"""

    def __init__(self, uid, username, password):
        """
        create new logged-in user
        :param uid: string represent user id for the user
        :param username: string represent username for the user
        :param password: string represent token / password for the user
        """
        self.uid = uid
        self.username = username
        self.password = password

    # def post_msg(self, recv_username, msg_content):
    #     msg_info = {
    #         'sender_id': self.uid,
    #         'sender_pw': self.password,
    #         'recv_username': recv_username,
    #         'msg_content': msg_content
    #     }
    #     msg_info = json.dumps(msg_info)
    #
    #     send_header(SERVER_CODE['post_msg'], len(msg_info))
    #     client.send(msg_info.encode(FORMAT))
    #
    #     print(client.recv(10).decode(FORMAT))

    def get_msg(self, partner_username):
        sender_info = {
            'sender_id': self.uid,
            'sender_pw': self.password,
            'partner_username': partner_username,
        }
        sender_info = json.dumps(sender_info)

        send_header(SERVER_CODE['get_msg'], len(sender_info))
        client.send(sender_info.encode(FORMAT))

        # can be server err-code or chat size
        chat_size = int(client.recv(HEADER_SIZE * 2).decode(FORMAT).strip())
        if chat_size < 0:
            # sender id wrong (-1), sender pw wrong (-2), partner username wrong (-3)
            return chat_size  # chat_size is sever error code
        else:
            chat = client.recv(chat_size).decode(FORMAT)
            chat = json.loads(chat)

            return chat

    def __repr__(self):
        """
        printable form of AuthorizedUser obj
        :return: string repr AuthorizedUser obj
        """
        return f'AuthorizedUser class -- uid: {self.uid}, ' \
               f'username: {self.username}, ' \
               f'password: {self.password}'
