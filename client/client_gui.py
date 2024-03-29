import sys
from os import system
from termcolor import cprint

import client as cl


def log_in_gui():
    """
    Display log-in or sign-up prompt, do input validation as well as pass to client backend to check
    credential with the client. Re-asking if any error occur.

    :return: AuthorizedUser obj repr an authorized user that able to get and post messages
    """
    while True:
        option = input("Log In (l) or Sign Up (s): ")
        if option not in ['l', 's']:
            cprint("Please enter 'l' for log-in and 's' for sign-up.\n", color='yellow')
            continue
        else:
            username = input('Username: ').strip().replace(' ', '')
            password = input('Password: ').strip().replace(' ', '')

            if option == 'l':
                cl_resp = cl.log_in(username, password)
                if cl_resp == '-1':
                    cprint('No account with username', color='yellow', end=' ')
                    print(f'{username}\n')
                    continue
                elif cl_resp == '-2':
                    cprint('Password is incorrect.\n', color='yellow')
                    continue
                else:
                    cprint('Successfully logged-in as', color='green', end=" ")
                    print(username)
                    return cl_resp

            elif option == 's':
                cl_resp = cl.sign_up(username, password)
                if cl_resp == '-1':
                    cprint('The username ', color='yellow', end='')
                    print(username, end='')
                    cprint(' have been taken.\n', color='yellow')
                    continue
                else:
                    cprint('Successfully logged-in as', color='green', end=' ')
                    print(username)
                    return cl_resp


def conversation_gui(auth_user, chat):
    """
    Display the chat between 2 user

    :param auth_user: AuthorizedUser obj repr an authorized user
    :param chat: list of (mid, sender_id, recv_id, message_content), each repr a message between
        two users.
    """
    system('clear')
    cprint("-" * 32 + " Conversation View " + "-" * 32, color='cyan')
    print()

    for msg in chat:
        sender, recv, msg_content = msg[1:4]

        username_str_len = max(len(sender), len(recv), 7)
        sender_str = f'[{sender}]' + ' ' * (username_str_len - len(sender))

        if sender == auth_user.username:
            cprint(sender_str, color='green', end=' ')
        else:
            cprint(sender_str, color='yellow', end=' ')

        print(msg_content)

    print()
    cprint("-" * 30 + " End Conversation View " + "-" * 30, color='cyan')
    print()


def open_conversation_gui(auth_user, update=False, recv_username=None):
    """
    Prompt user to open a conversation with another existing user. Also do input validation.

    :param auth_user: AuthorizedUser obj repr an authorized user that able to get and post messages
    :param update: bool, if True, recv_username must be provided to update a displayed chat
    :param recv_username: str repr username of a recipient

    :return: str repr username of a recipient
    """
    while True:
        if update is True and recv_username is None:
            raise Exception('recv_username must be provided if update is True')
        elif update is False:
            recv_username = input("Open conversation with: ")
            recv_username = recv_username.strip().replace(' ', '')

        cl_resp = auth_user.get_msg(recv_username)
        if isinstance(cl_resp, int):
            if int(cl_resp) == -3:
                cprint('No account with username', color='yellow', end=' ')
                print(f'{recv_username}\n')

                update, recv_username = False, None
                continue
            else:
                cprint("App Compromise -- Unauthorized User", color='red')

                print("Closing Chat-App")
                cl.disconnect_from_server()

                sys.exit()
        else:
            conversation_gui(auth_user, cl_resp)
            return recv_username


def new_message_gui(auth_user, recv_username):
    """
    Prompt the user to enter their message to sent to another user. Double check if recipient is an
    existed user.

    :param auth_user: AuthorizedUser obj repr an authorized user that able post messages
    :param recv_username: str repr the username of the recipient

    :return: str repr the username of the recipient
    """
    while True:
        msg_content = input('Your message: ').strip()
        cl_resp = auth_user.post_msg(recv_username, msg_content)

        if int(cl_resp) == -3:
            cprint('No account with username', color='yellow', end=' ')
            print(f'{recv_username}\n')

            recv_username = input('Re-enter recipient username: ').strip()
            continue
        elif int(cl_resp) < 0:
            cprint("App Compromise -- Unauthorized User", color='red')

            print("Closing Chat-App")
            cl.disconnect_from_server()

            sys.exit()
        else:
            open_conversation_gui(auth_user, update=True, recv_username=recv_username)
            return recv_username


def main():
    """
    Start the client process. Call functions to give action prompt to user. Make sure disconnect
    with the server properly when closing the app.
    """
    try:
        print('Welcome to Chat-App')

        print()
        auth_user = log_in_gui()

        print()
        recv_username = open_conversation_gui(auth_user)

        while True:
            user_choice = input("Update (u), New Msg (m), \n"
                                "   New Convo (c), or Quit (q): ").strip()
            print()

            if len(user_choice) > 1 or user_choice not in ['u', 'm', 'c', 'q']:
                continue
            elif user_choice == 'u':
                open_conversation_gui(auth_user, update=True, recv_username=recv_username)
            elif user_choice == 'm':
                open_conversation_gui(auth_user, update=True, recv_username=recv_username)
                recv_username = new_message_gui(auth_user, recv_username)
            elif user_choice == 'c':
                recv_username = open_conversation_gui(auth_user)
            else:
                return

    except KeyboardInterrupt:
        pass

    finally:
        print('Closing Chat-App...')
        cl.disconnect_from_server()


main()
