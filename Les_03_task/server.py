from socket import *
import json
import argparse


def create_parcer():
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default='')
    parser.add_argument('-p', '--port', default=7777)
    return parser


def create_answer(code):
    if code == 200:
        answer_message = 'OK'
    elif code == 400:
        answer_message = 'Wrong JSON-object/ wrong request'
    elif code == 500:
        answer_message = 'Server ERROR'
    else:
        print('Wrong code')

    _answer = {
        "response": code,
        "alert": answer_message,
    }
    _json_answer = json.dumps(_answer)
    return _json_answer


def defenition_answer(message):
    if message['action'] == 'presence':
        return create_answer(200)


def read_message(message):
    try:
        received_message = json.loads(message)
        return defenition_answer(received_message)
    except:
        create_answer(400)


if __name__ == '__main__':
    parser = create_parcer()
    namespace = parser.parse_args()
    sock = socket(type=SOCK_STREAM)
    sock.bind((namespace.addr, int(namespace.port)))
    sock.listen(5)
    try:
        while True:
            connect, addr = sock.accept()
            data = connect.recv(1024)
            if not data:
                answer = create_answer(400)
            else:
                answer = read_message(data)
                print(answer)
            connect.send(answer.encode('utf-8'))
    finally:
        connect.close()