import json

from common.variables import ENCODING, MAX_PACKAGE_LENGTH
from common.decorators import log


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
        raise ValueError
    raise ValueError


@log
def send_message(sock, message):
    """
    Функция кодирования и отправки сообщения.
    """
    js_message = json.dumps(message)
    encoded_message = js_message.encode(ENCODING)
    sock.send(encoded_message)
