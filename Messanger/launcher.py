"""Лаунчер"""

import subprocess

p_list = []


while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        client_count = int(input('ведите количество клиентов для запуска: '))
        p_list.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(client_count):
            p_list.append(subprocess.Popen(f'python client.py -n',
                                           creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while p_list:
            VICTIM = p_list.pop()
            VICTIM.kill()
