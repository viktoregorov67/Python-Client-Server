"""Unit-тесты утилит"""

import os
import sys
import unittest
import json

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, ENCODING
from common.utils import get_message, send_message


class TestSocket:
    '''
    Тестовый класс тестирования отправки и получения сообщения
    '''

    def __init__(self, test_dict):
        self.test_dict = test_dict
        self.encoded_message = None
        self.recieved_message = None

    def send(self, message_send):
        json_test_message = json.dumps(self.test_dict)
        self.encoded_message = json_test_message.encode(ENCODING)
        self.recieved_message = message_send

    def recv(self, max_len):
        json_test_message = json.dumps(self.test_dict)
        return json_test_message.encode(ENCODING)


class Tests(unittest.TestCase):
    '''
    Тестовый класс, выполняющий тестирование
    '''
    test_dict_send = {
        ACTION: PRESENCE,
        TIME: 123456.123456,
        USER: {
            ACCOUNT_NAME: 'test_user'
        }
    }
    test_dict_recv_ok = {RESPONSE: 200}
    test_dict_recv_err = {RESPONSE: 400, ERROR: 'Bad Request'}

    def test_send_msg(self):
        '''
        Тест функции отправки
        :return:
        '''
        test_socket = TestSocket(self.test_dict_send)
        send_message(test_socket, self.test_dict_send)
        # Проверяем коррректность кодирования
        self.assertEqual(test_socket.encoded_message, test_socket.recieved_message)
        # Проверяем, если на выходе не словарь
        self.assertRaises(TypeError, send_message, test_socket, 1234)

    def test_get_msg(self):
        '''
        Тест функции приема сообщения
        :return:
        '''
        test_sock_ok = TestSocket(self.test_dict_recv_ok)
        test_sock_err = TestSocket(self.test_dict_recv_err)
        self.assertEqual(get_message(test_sock_ok), self.test_dict_recv_ok)
        self.assertEqual(get_message(test_sock_err), self.test_dict_recv_err)
