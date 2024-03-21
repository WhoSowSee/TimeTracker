import importlib
import os
import subprocess
import sys
import time

from tqdm import trange

from utils import green, red, white

if not os.path.exists('save.py'):
    with open('save.py', 'w', encoding='UTF-8') as file:
        file.write(
            f'saved = True\ntimestamp = {time.time()}\nactivities = []\n'
        )
import save

# ERROR_MESSAGE = f'\n{red}Неверный ввод{white}'
CONSOLE_COMMAND_CLEAR = 'cls' if os.name == 'nt' else 'clear'


# Если система Windows -> cls, иначе -> clear
def clear_screen() -> None:
    os.system(CONSOLE_COMMAND_CLEAR)


def date_request() -> int:
    options = (
        'Активности',
        'Активность за последние две недели',
        'Активность за все время',
        'Среднее время активности по неделям',
        'Активность в виде круга',
        'Завершить сессию (Ctrl + C)',
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
        except Exception as exc:
            input(f'\n{red}Неверный ввод\n{exc}{white}')
            clear_screen()
        except KeyboardInterrupt:
            clear_screen()
            sys.exit()  # Выход из main


def file_call(file_path: str) -> None:
    importlib.reload(save)

    if save.activities:
        for _ in trange(100, desc='Генерация графика'):
            time.sleep(0.03)
        subprocess.run(['python', file_path])
        clear_screen()
    else:
        input(f'\n{red}Список занятий пуст{white}')
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
        try:
            if activity_operation in file_paths:
                file_call(file_paths.get(activity_operation))
            elif activity_operation == 6:
                clear_screen()
                sys.exit()
            elif activity_operation == 1:
                subprocess.run(['python', 'tracker.py'])
                clear_screen()
        except KeyboardInterrupt:
            clear_screen()
            sys.exit()  # Чтобы полностью выйти из tracker


def main() -> None:
    while True:
        clear_screen()
        run_activity()


if __name__ == '__main__':
    main()
