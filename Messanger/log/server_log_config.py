# logging - стандартный модуль для организации логирования
import logging
import logging.config
import logging.handlers

# Можно выполнить более расширенную настройку логирования.
# Создаем объект-логгер с именем app.main:
logger = logging.getLogger('app.server')

# Создаем объект форматирования:
formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(message)s')

# Создаем файловый обработчик логирования (можно задать кодировку):
sfh = logging.handlers.TimedRotatingFileHandler('log/server.log', encoding='utf-8', interval=1, when='D')
sfh.setLevel(logging.DEBUG)
sfh.setFormatter(formatter)

# Добавляем в логгер новый обработчик событий и устанавливаем уровень логирования
logger.addHandler(sfh)
logger.setLevel(logging.DEBUG)
