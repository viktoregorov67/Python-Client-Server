"""Unit-тесты сервера"""

import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))

from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE, RESPONSE_DEFAULT_IP_ADDRESS
from server import process_client_message


class TestServer(unittest.TestCase):
    '''
    Класс с тестами
    '''
    err_dict = {
        RESPONSE_DEFAULT_IP_ADDRESS: 400,
        ERROR: 'Bad Request'
    }
    ok_dict = {RESPONSE: 200}

    def test_ok_check(self):
        """Проверка запроса на корректность"""
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Guest'}}), self.ok_dict)

    def test_no_action(self):
        """Ошибка если нет действия"""
        self.assertEqual(process_client_message({TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_no_user(self):
        """Тест если нет пользователя"""
        self.assertEqual(process_client_message({ACTION: PRESENCE, TIME: '1.1'}), self.err_dict)

    def test_wrong_action(self):
        """Ошибка если неизвестное действие"""
        self.assertEqual(process_client_message(
            {ACTION: 'Wrong', TIME: '1.1', USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)

    def test_unknown_user(self):
        """Проверяем если пользователь не Guest"""
        self.assertEqual(process_client_message(
            {ACTION: PRESENCE, TIME: 1.1, USER: {ACCOUNT_NAME: 'Unknown_User'}}), self.err_dict)

    def test_no_time(self):
        """Ошибка, если  запрос не содержит штампа времени"""
        self.assertEqual(process_client_message({ACTION: PRESENCE, USER: {ACCOUNT_NAME: 'Guest'}}), self.err_dict)
