import importlib
import os
import subprocess
import sys
import time

import rich
from rich.console import Console
from rich.markdown import Markdown
from rich.table import Table
from tqdm import trange

from utils import green, red, white

if not os.path.exists('save.py'):
    with open('save.py', 'w', encoding='UTF-8') as file:
        file.write('activities = []\n')
import save

CONSOLE_COMMAND_CLEAR = 'cls' if os.name == 'nt' else 'clear'
OPTIONS = (
    'Активности',
    'Таблица активности',
    'График активности за две недели',
    'График активности за все время',
    'График среднего времени активности по неделям',
    'График активности в виде круга',
    'Инструкция',
    'Завершить сессию (Ctrl + C)',
)
FILE_PATHS = {
    3: 'bar.py',
    4: 'map.py',
    5: 'density.py',
    6: 'circles.py',
}


# Если система Windows -> cls, иначе -> clear
def clear_screen() -> None:
    os.system(CONSOLE_COMMAND_CLEAR)


def date_request() -> int:
    while True:
        for ind, name in enumerate(OPTIONS, start=1):
            print(f'{green}{ind}{white}: {name}')
        try:
            activity_operation = int(input('\nВвод: '))
            if activity_operation in (1, 2, 3, 4, 5, 6, 7, 8):
                return activity_operation
            else:
                raise ValueError
        except Exception as exc:
            clear_screen()
        except KeyboardInterrupt:
            clear_screen()
            sys.exit()  # Выход из main


def call_activity_table() -> None:
    importlib.reload(save)
    if save.activities:
        table = Table(show_lines=True)
        table.add_column('Активность', justify='center', vertical='middle')
        table.add_column('Время', justify='center', vertical='middle')
        table.add_column(
            'Подпись', justify='center', width=30, overflow='fold'
        )

        for activity, _, date, caption in save.activities:
            table.add_row(activity, date, caption)

        print()
        Console().input(table)
    else:
        input(f'\n{red}Список занятий пуст{white}')
        clear_screen()


def call_file(file_path: str) -> None:
    # Для динамического обновления списка активностей во время выполнения программы
    importlib.reload(save)

    if save.activities:
        for _ in trange(100, desc='Генерация графика'):
            time.sleep(0.03)
        subprocess.run([sys.executable, file_path])
        clear_screen()
    else:
        input(f'\n{red}Список занятий пуст{white}')
        clear_screen()


def run_activity() -> None:
    while True:
        try:
            activity_operation: int = date_request()
            if activity_operation in FILE_PATHS:
                call_file(FILE_PATHS[activity_operation])
            elif activity_operation == 8:
                clear_screen()
                sys.exit()  # Выход из main
            elif activity_operation == 1:
                importlib.reload(save)
                subprocess.run([sys.executable, 'tracker.py'])
                clear_screen()
            elif activity_operation == 2:
                call_activity_table()
                clear_screen()
            elif activity_operation == 7:
                clear_screen()
                with open('instruction.md', 'r') as f:
                    markdown_text = f.read()
                rich.print(Markdown(markdown_text))
                input()
                clear_screen()
        except KeyboardInterrupt:
            clear_screen()
            # TODO: Сделать возможность выхода из tracker в main по Ctrl + C
            sys.exit()  # Полный выход из tracker


def main() -> None:
    while True:
        clear_screen()
        run_activity()


if __name__ == '__main__':
    main()
