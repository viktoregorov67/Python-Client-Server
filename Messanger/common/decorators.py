import sys
import logging
import log.server_log_config
import log.client_log_config
import inspect


if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


def log(func):
    """Декоратор"""
    def log_save(*args, **kwargs):
        """Обертка."""
        res = func(*args, **kwargs)
        logger.debug(f'Функция {func.__name__} была вызвана из функции {inspect.stack()[1][3]}'
                     f' с параметрами {args}, {kwargs}.')
        return res
    return log_save




