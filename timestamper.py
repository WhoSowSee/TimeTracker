from datetime import datetime
from time import mktime

# formats:
# data: 26.07.2023 12:48:19
# unix-time: 1690364899.123

timestamp = input("Введите unix-time метку или дату: ")

try:
    if timestamp.count(':'):
        # data -> unix-time
        print(
            f'Unix-time метка: {mktime(datetime.strptime(timestamp, "%d.%m.%Y %H:%M:%S").timetuple())}'
        )
    else:
        # unix-time -> data
        print(
            f'Дата: {datetime.fromtimestamp(float(timestamp)).strftime("%d.%m.%Y %H:%M:%S")}'
        )

except (ValueError, TypeError):
    ...
