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

from utils import GREEN, RED, WHITE

if not os.path.exists('save.py'):
    with open('save.py', 'w', encoding='UTF-8') as file:
        file.write('activities = []\n')
import save

CONSOLE_COMMAND_CLEAR = 'cls' if os.name == 'nt' else 'clear'
OPTIONS = {
    1: 'Активности',
    2: 'Таблица активности',
    3: 'Вертикальный график активности за две недели',
    4: 'Горизонтальный график активности за две недели',
    5: 'График активности за все время',
    6: 'График активности в виде круга',
    7: 'Инструкция',
    8: 'Завершить сессию (Ctrl + C)',
}
FILE_PATHS = {
    3: 'bar.py',
    4: 'barh.py',
    5: 'map.py',
    6: 'circles.py',
}


def clear_screen() -> None:
    os.system(CONSOLE_COMMAND_CLEAR)


def date_request() -> int:
    while True:
        for ind, name in OPTIONS.items():
            print(f'{GREEN}{ind}{WHITE}: {name}')
        try:
            activity_operation = int(input('\nВвод: '))
            if activity_operation in OPTIONS.keys():
                return activity_operation
            else:
                raise ValueError
        except Exception as exc:
            clear_screen()
        except KeyboardInterrupt:
            clear_screen()
            sys.exit()  # Выход из main


def call_activity_table() -> None:
    table = Table(show_lines=True)
    table.add_column('Активность', justify='center', vertical='middle')
    table.add_column('Время', justify='center', vertical='middle')
    table.add_column('Подпись', justify='center', width=30, overflow='fold')

    for activity, _, date, caption in save.activities:
        table.add_row(activity, date, caption)

    Console().input(table)


def call_file(file_path: str) -> None:
    if save.activities:
        for _ in trange(100, desc='Генерация графика'):
            time.sleep(0.02)
        subprocess.run([sys.executable, file_path])
        clear_screen()
    else:
        input(f'\n{RED}Список занятий пуст{WHITE}')
        clear_screen()


def run_activity() -> None:
    while True:
        importlib.reload(save)
        try:
            activity_operation: int = date_request()
            if activity_operation in FILE_PATHS:
                call_file(FILE_PATHS[activity_operation])
            match activity_operation:
                case 8:
                    clear_screen()
                    sys.exit()  # Выход из main
                case 1:
                    subprocess.run([sys.executable, 'tracker.py'])
                    clear_screen()
                case 2:
                    if save.activities:
                        clear_screen()
                        call_activity_table()
                        clear_screen()
                    else:
                        input(f'\n{RED}Список занятий пуст{WHITE}')
                        clear_screen()
                case 7:
                    clear_screen()
                    with open('instruction.md', 'r') as file:
                        markdown_text = file.read()
                    rich.print(Markdown(markdown_text))
                    input()
                    clear_screen()
        except KeyboardInterrupt:
            clear_screen()
            sys.exit()  # Полный выход из tracker


def main() -> None:
    while True:
        clear_screen()
        run_activity()


if __name__ == '__main__':
    main()
