# 2. Каждое из слов «class», «function», «method» записать в байтовом типе без преобразования
# в последовательность кодов (не используя методы encode и decode) и определить тип,
# содержимое и длину соответствующих переменных.

str_1 = b'class'
str_2 = b'function'
str_3 = b'method'

str_list = [str_1, str_2, str_3]

for el in str_list:
    print(el)
    print(type(el))
    print(len(el))
    print('-------')
