"""Лаунчер"""

import subprocess

p_list = []

while True:
    ACTION = input('Выберите действие: q - выход, '
                   's - запустить сервер и клиенты, x - закрыть все окна: ')

    if ACTION == 'q':
        break
    elif ACTION == 's':
        p_list.append(subprocess.Popen('python server.py', creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(2):
            p_list.append(subprocess.Popen('python client.py -m send',
                                           creationflags=subprocess.CREATE_NEW_CONSOLE))
        for i in range(3):
            p_list.append(subprocess.Popen('python client.py -m listen',
                                           creationflags=subprocess.CREATE_NEW_CONSOLE))
    elif ACTION == 'x':
        while p_list:
            VICTIM = p_list.pop()
            VICTIM.kill()
