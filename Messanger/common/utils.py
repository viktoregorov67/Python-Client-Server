"""Утилиты"""

import json
import sys
from common.variables import ENCODING, MAX_PACKAGE_LENGTH
from common.decorators import log
from common.errors import *

sys.path.append('../')

@log
def get_message(client):
    """
    Функция приёма и декодирования сообщения.
    """
    encoded_response = client.recv(MAX_PACKAGE_LENGTH)
    if isinstance(encoded_response, bytes):
        json_response = encoded_response.decode(ENCODING)
        response = json.loads(json_response)
        if isinstance(response, dict):
            return response
        raise IncorrectDataRecivedError
    raise IncorrectDataRecivedError


@log
def send_message(sock, message):
    """
    Функция кодирования и отправки сообщения.
    """
    if not isinstance(message, dict):
        raise NonDictInputError
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
