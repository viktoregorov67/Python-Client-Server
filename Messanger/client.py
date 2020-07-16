import json
import socket
import sys
import time
import argparse
import logging
import log.client_log_config

from common.utils import get_message, send_message
from common.variables import *
from common.decorators import log
from common.errors import *

# Инициализация логгера клиента
LOGGER = logging.getLogger('client')


@log
def create_arg_parser():
    """ Создаём парсер аргументов коммандной строки """
    parser = argparse.ArgumentParser()
    parser.add_argument('addr', default=DEFAULT_IP_ADDRESS, nargs='?')
    parser.add_argument('port', default=DEFAULT_PORT, type=int, nargs='?')
    parser.add_argument('-m', '--mode', default='listen', nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_mode = namespace.mode

    # Проверяем номер порта
    if server_port < 1024 or server_port > 65535:
        LOGGER.critical(f'Запуск сервера с параметром порта {server_port}.'
                        f'В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Проверяем режим работы
    if client_mode not in ('listen', 'send'):
        LOGGER.critical(f'Недопустимый режим работы {client_mode}. Допустимые режимы: listen, send.')
        sys.exit(1)

    return server_address, server_port, client_mode


@log
def message_from_server(message):
    """ Обработчик сообщений от других клиентов """
    if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and MESSAGE_TEXT in message:
        LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n {message[MESSAGE_TEXT]}')
        print(f'Получено сообщение от пользователя {message[SENDER]}:\n {message[MESSAGE_TEXT]}')
    else:
        LOGGER.error(f'Получено некорректное сообщение от сервера {message}')


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает у пользователя текст сообщения и отправляет его или завершает работу по команде"""
    message = input('Введите сообщение. Для выхода введите \'q!\': ')
    if message == 'q!':
        sock.close()
        LOGGER.info('Клиент завершил работу по команде')
        print('Вы завершили работу. Ждем Вас снова!')
        sys.exit(0)
    message_dic = {
        ACTION: MESSAGE,
        TIME: time.time(),
        ACCOUNT_NAME: account_name,
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Сформировано сообщение: {message_dic}')
    return message_dic


@log
def create_presence(account_name='Guest'):
    """Функция генерирует запрос о присутствии клиента."""
    out = {
        ACTION: PRESENCE,
        TIME: time.ctime(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def process_ans(message):
    """Функция разбирает ответ сервера."""
    LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        return f'400 : {message[ERROR]}'
    raise ValueError


def main():
    # Проверяем параметры командной строки
    server_address, server_port, client_mode = create_arg_parser()

    LOGGER.info(f'Программа клиента запущена в режиме {client_mode}.')

    # Инициализация сокета и обмен.
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence())
        answer = process_ans(get_message(transport))
        LOGGER.info(f'Соединенеие с сервером установлено. Ответ от сервера: {answer}.')
        print('Соединенеие с сервером установлено.')
    except json.JSONDecodeError:
        LOGGER.error('Не удалось декодировать сообщение сервера.')
        sys.exit(1)
    except ServerError as error:
        LOGGER.error(f'Ошибка соединения с сервером. Сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except ConnectionRefusedError:
        LOGGER.critical(f'Не удалось подключиться к серверу {server_address} по порту {server_port}')
        sys.exit(1)
    else:
        if client_mode == 'send':
            print('Работа в режиме отправки сообщений')
        else:
            print('Работа в режиме приёма сообщений')
        while True:
            if client_mode == 'send':
                try:
                    send_message(transport, create_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOGGER.error(f'Соединение с сервером {server_address} потеряно.')
                    sys.exit(1)

            if client_mode == 'listen':
                try:
                    message_from_server(get_message(transport))
                except (ConnectionResetError, ConnectionError, ConnectionAbortedError):
                    LOGGER.error(f'Соединение с сервером {server_address} потеряно.')
                    sys.exit(1)


if __name__ == '__main__':
    main()
