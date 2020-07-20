"""Unit-тесты клиентской части"""

import os
import sys
import unittest

sys.path.append(os.path.join(os.getcwd(), '..'))
from common.variables import RESPONSE, ERROR, USER, ACCOUNT_NAME, TIME, ACTION, PRESENCE
from client import create_presence, process_ans


class TestClass(unittest.TestCase):
    '''
    Класс с тестами
    '''

    def test_def_presense(self):
        """Тест коректного запроса"""
        test = create_presence()
        test[TIME] = 1.2
        self.assertEqual(test, {ACTION: PRESENCE, TIME: 1.2, USER: {ACCOUNT_NAME: 'Guest'}})

    def test_answer_200(self):
        """Тест корректтного разбора ответа 200"""
        self.assertEqual(process_ans({RESPONSE: 200}), '200 : OK')

    def test_answer_400(self):
        """Тест корректного разбора ответа 400"""
        self.assertEqual(process_ans({RESPONSE: 400, ERROR: 'Bad Request'}), '400 : Bad Request')

    def test_no_response(self):
        """Тест исключения без поля RESPONSE"""
        self.assertRaises(ValueError, process_ans, {ERROR: 'Bad Request'})
