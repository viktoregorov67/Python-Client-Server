import json
import socket
import sys
import logging
import log.server_log_config

from common.utils import get_message, send_message
from common.variables import (
    ACCOUNT_NAME, ACTION, DEFAULT_PORT, ERROR, MAX_CONNECTIONS, PRESENCE,
    RESPONSE_DEFAULT_IP_ADDRESS, RESPONSE, TIME, USER)
from common.decorators import log


# Инициализация логгера сервера
SERVER_LOGGER = logging.getLogger('server')


@log
def process_client_message(message):
    """
    Обработчик сообщений от клиентов
    """
    if (
            ACTION in message and
            message[ACTION] == PRESENCE and
            TIME in message and
            USER in message and
            message[USER][ACCOUNT_NAME] == 'Guest'
    ):
        return {
            RESPONSE: 200
        }
    return {
        RESPONSE_DEFAULT_IP_ADDRESS: 400,
        ERROR: 'Bad Request'
    }


def main():
    # Загружаем, какой адрес слушать.

    try:
        if '-a' in sys.argv:
            listen_address = sys.argv[sys.argv.index('-a') + 1]
        else:
            listen_address = ''

    except IndexError:
        SERVER_LOGGER.error('Необходимо указать адрес, который будет слушать сервер после параметра -\'a\'.')
        sys.exit(1)

    # Загружаем, на какой порт обращаться.
    try:
        if '-p' in sys.argv:
            listen_port = int(sys.argv[sys.argv.index('-p') + 1])
        else:
            listen_port = DEFAULT_PORT
        if listen_port < 1024 or listen_port > 65535:
            raise ValueError
    except IndexError:
        SERVER_LOGGER.error('Необходимо указать номер порта после параметра -\'p\'.')
        sys.exit(1)
    except ValueError:
        SERVER_LOGGER.debug('В качестве порта может быть указано только число в диапазоне от 1024 до 65535.')
        sys.exit(1)

    # Готовим сокет
    transport = socket.socket()
    transport.bind((listen_address, listen_port))
    # Слушаем порт
    transport.listen(MAX_CONNECTIONS)

    while True:
        client, client_address = transport.accept()
        try:
            message_from_client = get_message(client)
            SERVER_LOGGER.info(f'Получено сообщение {message_from_client}')
            response = process_client_message(message_from_client)
            send_message(client, response)
            client.close()
        except (ValueError, json.JSONDecodeError):
            SERVER_LOGGER.debug(f'Принято некорретное сообщение от клиента {client_address}.')
            client.close()


if __name__ == '__main__':
    SERVER_LOGGER.info('Сервер запущен')
    main()
