import os
import subprocess
import sys
import time

from tqdm import tqdm

from utils import green, red, white


# Если система Windows -> cls, иначе -> clear
def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')


def date_request() -> int:
    options = (
        'Добавить занятия',
        'Посмотреть активность за последние две недели',
        'Посмотреть активность за все время',
        'Посмотреть среднее время активности по неделям',
        'Посмотреть активность в виде круга',
        'Завершить сессию',
    )

    while True:
        for ind, name in enumerate(options, start=1):
            print(f'{green}{ind}{white}: {name}')

        try:
            activity_operation = int(input('\nВвод: '))
            if activity_operation in (1, 2, 3, 4, 5, 6):
                return activity_operation
            else:
                raise ValueError
        except ValueError:
            input(f'\n{red}Неверный ввод{white}')
            clear_screen()


def file_call(file_path: str) -> None:
    with tqdm(total=100, desc='Генерация изображения') as f:
        for i in range(5):
            time.sleep(0.4)
            f.update(20)
    subprocess.run(['python', file_path])

    clear_screen()


def run_activity() -> None:
    file_paths = {
        2: 'bar.py',
        3: 'map.py',
        4: 'density.py',
        5: 'circles.py',
    }
    while True:
        activity_operation: int = date_request()

        if activity_operation in file_paths:
            file_call(file_paths.get(activity_operation))
        elif activity_operation == 6:
            clear_screen()
            sys.exit()
        elif activity_operation == 1:
            subprocess.run(['python', 'tracker.py'])
            clear_screen()


def main():
    while True:
        clear_screen()
        run_activity()


if __name__ == '__main__':
    main()
