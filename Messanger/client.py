import json
import socket
import sys
import time
import argparse
import threading
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
    parser.add_argument('-n', '--name', default=None, nargs='?')
    namespace = parser.parse_args(sys.argv[1:])
    server_address = namespace.addr
    server_port = namespace.port
    client_name = namespace.name

    # Проверяем номер порта
    if server_port < 1024 or server_port > 65535:
        LOGGER.critical(f'Запуск сервера с параметром порта {server_port}.'
                        f'В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    return server_address, server_port, client_name


@log
def message_from_server(sock, my_username):
    """ Обработчик сообщений от других клиентов, поступающих с сервера """
    while True:
        try:
            message = get_message(sock)
            if ACTION in message and message[ACTION] == MESSAGE and SENDER in message and \
                    SENDER in message and MESSAGE_TEXT in message and message[DESTINATION] == my_username:
                LOGGER.info(f'Получено сообщение от пользователя {message[SENDER]}:\n {message[MESSAGE_TEXT]}')
                print(f'Получено сообщение от пользователя {message[SENDER]}:\n {message[MESSAGE_TEXT]}')
            else:
                LOGGER.error(f'Получено некорректное сообщение от сервера {message}')
        except IncorrectDataRecivedError:
            LOGGER.error(f'Не удалось декодировать сообщение')
        except (OSError, ConnectionError, ConnectionAbortedError, ConnectionResetError, json.JSONDecodeError):
            LOGGER.critical(f'Соедиение с сервером потеряно')
            break


@log
def create_message(sock, account_name='Guest'):
    """Функция запрашивает у пользователя текст сообщения и отправляет его или завершает работу по команде"""
    to_user = input('Введите получателя сообщения: ')
    message = input('Введите сообщение: ')
    message_dic = {
        ACTION: MESSAGE,
        SENDER: account_name,
        DESTINATION: to_user,
        TIME: time.time(),
        MESSAGE_TEXT: message
    }
    LOGGER.debug(f'Сформировано сообщение: {message_dic}')
    try:
        send_message(sock, message_dic)
        LOGGER.info(f'Сообщение отправлено клиенту {to_user}')
    except:
        LOGGER.info('Соединение с сервером потеряно')
        sys.exit(1)


@log
def create_presence(account_name='Guest'):
    """Функция генерирует запрос о присутствии клиента."""
    out = {
        ACTION: PRESENCE,
        TIME: time.time(),
        USER: {
            ACCOUNT_NAME: account_name
        }
    }
    LOGGER.debug(f'Сформировано {PRESENCE} сообщение для пользователя {account_name}')
    return out


@log
def create_message_exit(account_name):
    """Функция создает словарь с соббщением о выходе"""
    return {
        ACTION: EXIT,
        TIME: time.time(),
        ACCOUNT_NAME: account_name
    }


@log
def user_interactive(sock, username):
    """Функция взаимодействия с пользователем, запрашивает команды, отправляет сообщения"""
    print_help()
    while True:
        command = input('Введите команду: ')
        if command == 'message':
            create_message(sock, username)
        elif command == 'help':
            print_help()
        elif command == 'exit':
            send_message(sock, create_message_exit(username))
            print('Завершение соединения.')
            LOGGER.info('Завершение работы по команде пользователя.')
            # Задержка неоходима, чтобы успело уйти сообщение о выходе
            time.sleep(0.5)
            break
        else:
            print('Команда не распознана, попробойте снова. help - вывести поддерживаемые команды.')


def print_help():
    """Функция выводящяя справку по использованию"""
    print('Поддерживаемые команды:')
    print('message - отправить сообщение. Кому и текст будет запрошены отдельно.')
    print('help - вывести подсказки по командам')
    print('exit - выход из программы')


@log
def process_ans(message):
    """Функция разбирает ответ сервера."""
    LOGGER.debug(f'Разбор сообщения от сервера: {message}')
    if RESPONSE in message:
        if message[RESPONSE] == 200:
            return '200 : OK'
        elif message[RESPONSE] == 400:
            raise ServerError(f'400 : {message[ERROR]}')
    raise ReqFieldMissingError(RESPONSE)


def main():
    # Проверяем параметры командной строки
    server_address, server_port, client_name = create_arg_parser()

    # Если имя пользователя не было задано, необходимо запросить пользователя.
    if not client_name:
        client_name = input('Введите имя пользователя: ')

    LOGGER.info(
        f'Запущен клиент с парамертами: адрес сервера: {server_address}, '
        f'порт: {server_port}, имя пользователя: {client_name}')

    # Инициализация сокета и обмен.
    try:
        transport = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        transport.connect((server_address, server_port))
        send_message(transport, create_presence(client_name))
        answer = process_ans(get_message(transport))
        LOGGER.info(f'Соединенеие с сервером установлено. Ответ от сервера: {answer}.')
        print('Соединенеие с сервером установлено.')
    except json.JSONDecodeError:
        LOGGER.error('Не удалось декодировать сообщение сервера.')
        sys.exit(1)
    except ServerError as error:
        LOGGER.error(f'Ошибка соединения с сервером. Сервер вернул ошибку: {error.text}')
        sys.exit(1)
    except (ConnectionRefusedError, ConnectionError):
        LOGGER.critical(f'Не удалось подключиться к серверу {server_address}:{server_port}')
        sys.exit(1)
    else:
        # Соединение с сервером установлено корректно. Запускаем процесс приема сообщений
        reciever = threading.Thread(target=message_from_server, args=(transport, client_name))
        reciever.daemon = True
        reciever.start()
        # Процесс отправки сообщений и взаимодействия с пользователем
        user_interface = threading.Thread(target=user_interactive, args=(transport, client_name))
        user_interface.daemon = True
        user_interface.start()

        LOGGER.info('Процессы пользователя запущены')

        while True:
            time.sleep(1)
            if reciever.is_alive() and user_interface.is_alive():
                continue
            break


if __name__ == '__main__':
    main()
