# 4. Преобразовать слова «разработка», «администрирование», «protocol», «standard» из строкового
# представления в байтовое и выполнить обратное преобразование (используя методы encode и decode).

var_1 = 'разработка'
var_2 = 'администрирование'
var_3 = 'protocol'
var_4 = 'standard'

var_list = [var_1, var_2, var_3, var_4]

var_bytes = []
for el in var_list:
    el_bytes = el.encode('utf-8')
    var_bytes.append(el_bytes)

print(var_bytes)

var_str = []
for el in var_bytes:
    el_str = el.decode('utf-8')
    var_str.append(el_str)

print(var_str)
