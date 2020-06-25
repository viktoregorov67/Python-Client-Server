from socket import *
import json
import time
import argparse

client = 'client'
status = 'OK'


def create_parcer():
    '''
    Create named arguments for run client.
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default='localhost')
    parser.add_argument('-p', '--port', default=7777)
    return parser


def presence_message():
    """
    Create presence request
    retract json object
    """
    message = {
        'action': 'presence',
        'time': time.ctime(),
        'type': 'status',
        'user': {
            'account_name': client,
            'status': status,
        }
    }
    return json.dumps(message)


def read_message(message):
    try:
        received_message = json.loads(message)
        return defenition_answer(received_message)
    except:
        pass


def defenition_answer(message):
    if message['action'] == 'probe':
        message_for_server = presence_message()
        s.send(message_for_server.encode('utf-8'))


if __name__ == '__main__':
    parser = create_parcer()
    namespace = parser.parse_args()
    s = socket(AF_INET, SOCK_STREAM)
    s.connect((namespace.addr, int(namespace.port)))
    message_for_server = presence_message()
    s.send(message_for_server.encode('utf-8'))
    response = s.recv(1024)
    read_message(response)
    print(f'Ответ: {response.decode("utf-8")}')