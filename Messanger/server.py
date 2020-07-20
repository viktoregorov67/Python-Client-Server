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
def process_client_message(message, message_list, client, clients, names):
    """ Обработчик сообщений от клиентов """
    LOGGER.debug(f'Разбор сообщения от клиента : {message}')
    # Если это сообщение о присутствии, принимаем и отвечаем
    if ACTION in message and message[ACTION] == PRESENCE and TIME in message and USER in message:
        if message[USER][ACCOUNT_NAME] not in names.keys():
            names[message[USER][ACCOUNT_NAME]] = client
            send_message(client, RESPONSE_200)
        else:
            response = RESPONSE_400
            response[ERROR] = 'Имя пользователя занято.'
            send_message(client, response)
            clients.remove(client)
            client.close()
        return
    elif ACTION in message and message[ACTION] == MESSAGE and TIME in message and \
            DESTINATION in message and SENDER in message and MESSAGE_TEXT in message:
        message_list.append(message)
        return
    # Если клиент выходит
    elif ACTION in message and message[ACTION] == EXIT and ACCOUNT_NAME in message:
        clients.remove(names[message[ACCOUNT_NAME]])
        names[message[ACCOUNT_NAME]].close()
        del names[message[ACCOUNT_NAME]]
        return
    else:
        response = RESPONSE_400
        response[ERROR] = 'Запрос некорректен.'
        send_message(client, response)
        return


@log
def process_message(message, names, listen_socks):
    """
    Функция адресной отправки сообщения определённому клиенту. Принимает словарь сообщение,
    список зарегистрированых пользователей и слушающие сокеты. Ничего не возвращает.
    :param message:
    :param names:
    :param listen_socks:
    :return:
    """
    if message[DESTINATION] in names and names[message[DESTINATION]] in listen_socks:
        send_message(names[message[DESTINATION]], message)
        LOGGER.info(f'Отправлено сообщение пользователю {message[DESTINATION]} '
                    f'от пользователя {message[SENDER]}.')
    elif message[DESTINATION] in names and names[message[DESTINATION]] not in listen_socks:
        raise ConnectionError
    else:
        LOGGER.error(
            f'Пользователь {message[DESTINATION]} не зарегистрирован на сервере, '
            f'отправка сообщения невозможна.')


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
    # Словарь имен пользователей и соответствующие сокеты
    names = dict()
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
                    process_client_message(get_message(client_with_msg), messages, client_with_msg,
                                           clients, names)
                except:
                    LOGGER.info(f'Пользователь {client_with_msg.getpeername()} отключился.')
                    clients.remove(client_with_msg)

        # Если есть сообщения, то обрабатываем каждое.
        for i in messages:
            try:
                process_message(i, names, send_lst)
            except Exception:
                LOGGER.info(f'Связь с клиентом с именем {i[DESTINATION]} была потеряна')
                clients.remove(names[i[DESTINATION]])
                del names[i[DESTINATION]]
        messages.clear()


if __name__ == '__main__':
    main()
