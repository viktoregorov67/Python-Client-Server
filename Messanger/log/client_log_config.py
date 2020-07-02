# logging - стандартный модуль для организации логирования
import logging
import logging.config

# Можно выполнить более расширенную настройку логирования.
# Создаем объект-логгер с именем app.main:
logger = logging.getLogger('app.client')

# Создаем объект форматирования:
formatter = logging.Formatter('%(asctime)s %(levelname)s %(module)s %(message)s')

# Создаем файловый обработчик логирования (можно задать кодировку):
cfh = logging.FileHandler('log/client.log', encoding='utf-8')
cfh.setLevel(logging.DEBUG)
cfh.setFormatter(formatter)

# Добавляем в логгер новый обработчик событий и устанавливаем уровень логирования
logger.addHandler(cfh)
logger.setLevel(logging.DEBUG)
