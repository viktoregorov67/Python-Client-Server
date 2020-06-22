"""
1. Задание на закрепление знаний по модулю CSV. Написать скрипт, осуществляющий выборку определенных данных
из файлов info_1.txt, info_2.txt, info_3.txt и формирующий новый «отчетный» файл в формате CSV.
Для этого:
 - Создать функцию get_data(), в которой в цикле осуществляется перебор файлов с данными, их открытие и
 считывание данных. В этой функции из считанных данных необходимо с помощью регулярных выражений извлечь
 значения параметров «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
 - Значения каждого параметра поместить в соответствующий список. Должно получиться четыре списка —
 например, os_prod_list, os_name_list, os_code_list, os_type_list.
 - В этой же функции создать главный список для хранения данных отчета — например, main_data — и поместить в него
 названия столбцов отчета в виде списка: «Изготовитель системы», «Название ОС», «Код продукта», «Тип системы».
 - Значения для этих столбцов также оформить в виде списка и поместить в файл main_data (также для каждого файла).
 - Создать функцию write_to_csv(), в которую передавать ссылку на CSV-файл. В этой функции реализовать получение
 данных через вызов функции get_data(), а также сохранение подготовленных данных в соответствующий CSV-файл.
"""

import csv
import re


def get_data():
    os_prod_list = []
    os_name_list = []
    os_code_list = []
    os_type_list = []
    main_data = []

    for i in range(1, 4):
        file_obj = open(f'info_{i}.txt', encoding='utf-8')
        data = file_obj.read()

        os_prod = re.compile(r'Изготовитель системы:\s*\S*')
        os_prod_list.append(os_prod.findall(data)[0].split()[2])

        os_name = re.compile(r'Windows\s*\S*\s*\S*')
        os_name_list.append(os_name.findall(data)[0])

        os_code = re.compile(r'Код продукта:\s*\S*')
        os_code_list.append(os_code.findall(data)[0].split()[2])

        os_type = re.compile(r'Тип системы:\s*\S*')
        os_type_list.append(os_type.findall(data)[0].split()[2])

    headers = ['Изготовитель системы', 'Название ОС', 'Код продукта', 'Тип системы']
    main_data.append(headers)

    for i in range(0, 3):
        row_data = [os_prod_list[i], os_name_list[i], os_code_list[i], os_type_list[i]]
        main_data.append(row_data)
    return main_data


def write_to_csv(out_file):
    main_data = get_data()
    with open(out_file, 'w', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerows(main_data)


write_to_csv('data_report.csv')
