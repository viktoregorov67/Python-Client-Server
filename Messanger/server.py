import json
import socket
import sys
import select
import logging
import argparse
import time
import log.server_log_config

from common.utils import get_message, send_message
from common.variables import *
from common.decorators import log

# Инициализация логгера сервера
LOGGER = logging.getLogger('server')


@log
def process_client_message(message, message_list, client):
    """ Обработчик сообщений от клиентов """
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message \
            and message[USER][ACCOUNT_NAME] == 'Guest':
        send_message(client, {RESPONSE: 200})
        return
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and \
            MESSAGE_TEXT in message:
        message_list.append((message[ACCOUNT_NAME], message[MESSAGE_TEXT]))
        return
    else:
        send_message(client, {
            RESPONSE: 400,
            ERROR: 'Bad Request'
        })
        return


@log
def create_arg_parser():
    """ Создаём парсер аргументов коммандной строки """
    parser = argparse.ArgumentParser()
    parser.add_argument('-a', '--addr', default='', nargs='?')
    parser.add_argument('-p', '--port', default=DEFAULT_PORT, type=int, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    listen_address = namespace.addr
    listen_port = namespace.port

    # Проверяем номер порта
    if listen_port < 1024 or listen_port > 65535:
        LOGGER.critical(f'Запуск сервера с параметром порта {listen_port}.'
                        f'В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    return listen_address, listen_port


def main():
    # Проверяем параметры командной строки
    listen_address, listen_port = create_arg_parser()

    LOGGER.info(
        f'Сервер запущен. Порт для подключений: {listen_port}.'
        f'Адрес с котрого принимаются сообщения: {listen_address}. '
    )

    # Готовим сокет
    transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    transport.bind((listen_address, listen_port))
    transport.settimeout(0.2)
    # Устанавливаем список клиентов и очередь сообщений
    clients = []
    messages = []

    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)

    while True:
        try:
            client, client_address = transport.accept()
        except OSError:
            pass
        else:
            LOGGER.info(f'Клиент {client_address} подключился.')
            clients.append(client)

        recv_lst = []
        send_lst = []
        err_lst = []

        try:
            if clients:
                recv_lst, send_lst, err_lst = select.select(clients, clients, [], 0)
        except OSError:
            pass

        # Принимаем сообщения и если они есть, то заполняем словарь, если ошибка - отключаем клиента
        if recv_lst:
            for client_with_msg in recv_lst:
                try:
                    process_client_message(get_message(client_with_msg), messages, client_with_msg)
                except:
                    LOGGER.info(f'Пользователь {client_with_msg.getpeername()} отключился.')
                    clients.remove(client_with_msg)

        # Если есть сообщения для отправки и ожидающие клиенты, отправляем им сообщение.
        if messages and send_lst:
            message = {
                ACTION: MESSAGE,
                SENDER: messages[0][0],
                TIME: time.time(),
                MESSAGE_TEXT: messages[0][1]
            }
            del messages[0]
            for wait_client in send_lst:
                try:
                    send_message(wait_client, message)
                except:
                    LOGGER.info(f'Пользователь {wait_client.getpeername()} отключился.')
                    clients.remove(wait_client)


if __name__ == '__main__':
    main()
