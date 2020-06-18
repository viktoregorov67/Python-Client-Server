# 5. Выполнить пинг веб-ресурсов yandex.ru, youtube.com и преобразовать результаты из байтовового в
# строковый тип на кириллице.

import subprocess
import chardet

args = ['ping', 'yandex.ru']
YA_PING = subprocess.Popen(args, stdout=subprocess.PIPE)

for line in YA_PING.stdout:
    result = chardet.detect(line)
    data = line.decode(result['encoding']).encode('utf-8')
    print(data.decode('utf-8'))

args_2 = ['ping', 'youtube.com']
YOUT_PING = subprocess.Popen(args_2, stdout=subprocess.PIPE)

for line in YOUT_PING.stdout:
    result = chardet.detect(line)
    data = line.decode(result['encoding']).encode('utf-8')
    print(data.decode('utf-8'))
