import os
from datetime import datetime, timedelta
from os import makedirs, path, system
from time import time

from setup import setup
from utils import (
    CYAN,
    GREEN,
    HOUR,
    MAGENTA,
    MINUTE,
    RED,
    SECOND,
    WHITE,
    generate_activities_times,
)

saved = True
timestamp: float = time()
activities = []
from save import *

ARGS, ACTIVITIES = setup('tracker')
weeks = (timestamp - activities[0][1]) // (7 * 24 * HOUR) if activities else 0
CONSOLE_COMMAND_CLEAR = 'cls' if os.name == 'nt' else 'clear'


def clear_screen() -> None:
    system(CONSOLE_COMMAND_CLEAR)


def data_save(saved=True) -> None:
    with open('save.py', 'w', encoding='UTF-8') as file:
        file.write(f'{saved = }\n{timestamp = }\n')
        if not activities:
            file.write('activities = []\n')
        else:
            file.write('activities = [\n')
            for i in activities:
                file.write(f'\t{i},\n')
            file.write(']\n')

    # Weekly dump
    global weeks
    if saved and activities:
        if (timestamp - activities[0][1]) // (7 * 24 * HOUR) > weeks:
            weeks += 1

            filename = (
                f'./dumps/week-{round(weeks)} ({activities[-1][2][:10]}).py'
            )
            makedirs(path.dirname(filename), exist_ok=True)

            with open(filename, 'w') as file:
                file.write(
                    f'{saved = }\ntimestamp = {activities[0][1] + weeks * 7 * 24 * HOUR}\n'
                )
                if not activities:
                    file.write('activities = []\n')
                else:
                    file.write('activities = [\n')
                    for i in activities:
                        file.write(f'\t{i},\n')
                    file.write(']\n')


def stages_formatter(stages: int, verb=0) -> str:
    """
    Функция, которая форматирует вывод числа stages в соответствии с правилами русского языка для согласования числительных и существительных.
    """
    if verb:
        form = ['этапа', 'этапов', 'этапов']
    else:
        form = ['этап', 'этапа', 'этапов']

    last_digit = int(str(stages)[-1])
    last_2_digits = int(str(stages)[-2:])

    if last_digit == 1 and last_2_digits != 11:
        return f'{MAGENTA}{stages}{WHITE} {form[0]}'

    if 1 <= last_digit <= 4 and (last_2_digits < 10 or last_2_digits > 20):
        return f'{MAGENTA}{stages}{WHITE} {form[1]}'

    return f'{MAGENTA}{stages}{WHITE} {form[2]}'


def analytics() -> None:
    if not activities:
        return

    sum_all = timestamp - activities[0][1]
    print(
        f'Итоги {stages_formatter(len(activities), 1)} '
        f'({CYAN}{timedelta(0, round(sum_all))}{WHITE})'
    )
    print()
    activities_times = generate_activities_times(activities, timestamp)
    save_activities = set([i[0] for i in activities])

    # Analyze all data
    for activity_name in ACTIVITIES:
        if activity_name not in save_activities:
            continue

        activity_time = sum(activities_times[activity_name])
        if activity_time == 0:
            continue

        activity_percentage = activity_time / sum_all * 100
        activity_counter = len(activities_times[activity_name])
        activity_mean = activity_time / activity_counter

        print(
            f'{activity_name} ({stages_formatter(activity_counter)}) ({round(activity_percentage, 2)}%)\n'
            f'Всего: {CYAN}{timedelta(0, round(activity_time))}{WHITE}\n'
            f'В среднем {CYAN}{timedelta(0, round(activity_mean))}{WHITE} за этап\n'
        )
    input()


def clear_activities() -> None:
    global activities
    activities.clear()
    data_save()
    input(f'\n{CYAN}Все занятия удалены{WHITE}')
    clear_screen()


# Error checking
if not saved:
    input(
        f'Последняя сессия была прервана: {activities[-1][0]} ({activities[-1][2]})'
    )
    input(
        f'Добавление потерянного времени: {CYAN}+{timedelta(0, int(time() - timestamp))}{WHITE}\n'
    )

    timestamp: float = time()
    data_save()


while True:
    clear_screen()

    timestamp = time()
    # Header
    activity = len(activities)
    stageline = f'{RED}Список занятий пуст{WHITE}'

    if activities:
        stageline = (
            f"Этап {MAGENTA}{activity}{WHITE}, {activities[-1][0]} "
            f"({datetime.fromtimestamp(timestamp).strftime('%H:%M:%S')}) "
            f"({CYAN}{timedelta(0, round(timestamp - activities[-1][1]))}{WHITE})\n"
        )
        print(stageline)
    # Activities

    print('Выбор занятия:')
    for i, name in enumerate(ACTIVITIES, start=1):
        print(f'{GREEN}{i}{WHITE}: {name}')

    print()

    for ind, name in enumerate(
        (
            'Завершить сессию',
            'Удалить последнее занятие',
            'Изменить время последнего занятия',
            'Добавить подпись к последнему занятию',
            'Удалить все занятия',
        )
    ):
        print(f"{GREEN}{'edcif'[ind]}{WHITE}: {name}")

    # Gain input
    try:
        session_id = input('\nВвод: ')
    except KeyboardInterrupt:
        exit()  # Первый этап выхода из tracker
    except Exception as exc:
        print()
        input(f'\n{RED}Неверный ввод{WHITE}')
        continue

    if session_id.isdigit():
        session_id = int(session_id)
    elif session_id in ('e', 'd', 'c', 'i', 'f'):
        session_id = len(ACTIVITIES) + 'edcif'.index(session_id) + 1
    else:
        session_id = 0

    print()

    # Create new session
    if 1 <= session_id <= len(ACTIVITIES):
        activity_name = list(ACTIVITIES.keys())[session_id - 1]

        # If activity repeat
        if activities and activity_name == activities[-1][0]:
            print(
                f'Продолжение предыдущей сессии -> {activities[-1][0]} ({activities[-1][2]})'
            )
            note = activities[-1][3]

        else:
            note = ''
            if activity_name == ARGS['ANOTHER']:
                note = input('Подпись: ') or (ARGS['ANOTHER_DEFAULT_NOTE'])

            # TODO: Test
            current_time = time()  # Получаем текущее время
            activities.append(
                [
                    f'{activity_name}',
                    current_time,  # Используем текущее время в качестве времени начала активности
                    f"{datetime.fromtimestamp(current_time).strftime('%d.%m.%Y %H:%M:%S')}",
                    note,
                ]
            )

            # Вычисление длительности активности
            activity_duration = (
                current_time - activities[-1][1]
            )  # Разница между текущим временем и временем начала активности
            activity_lasts = timedelta(seconds=round(activity_duration))

            # activities.append(
            #     [
            #         f'{activity_name}',
            #         timestamp,
            #         f"{datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M:%S')}",
            #         note,
            #     ]
            # )

        # Wait for input to end session
        data_save(saved=False)
        input(f"<< {activity_name}{'' if not note else ' (' + note + ')'} >>")

        timestamp: float = time()

    # End session
    if session_id == len(ACTIVITIES) + 1:
        data_save()
        analytics()
        exit()

    # Delete last activity
    if session_id == len(ACTIVITIES) + 2:
        if not activities:
            input(stageline)
        else:
            print(f'Удалить: {activities[-1][0]} ({activities[-1][2]})?')
            if input('y/n: ').lower() == 'y':
                activities.pop()

                input(f'\n{CYAN}Занятие удалено{WHITE}')
            else:
                input(f'\n{RED}Удаление отменено{WHITE}')

    # Change last activity time
    if session_id == len(ACTIVITIES) + 3:
        if not activities:
            input(stageline)
        else:
            activity_name = activities[-1][0]
            activity_start_time = activities[-1][2]
            activity_lasts = timedelta(0, round(timestamp - activities[-1][1]))

            print(
                f'Формат ввода времени: {GREEN}15*HOUR + 4*MINUTE + 12*SECOND{WHITE} ({CYAN}HOUR{WHITE} - часы, {CYAN}MINUTE{WHITE} - минуты, {CYAN}SECOND{WHITE} - секунды)\n'
            )
            print(
                f'Последний этап: {activity_name} ({activity_start_time}) {CYAN}{activity_lasts}{WHITE}'
            )
            try:
                allocated_time = eval(input('Этап закончился раньше на: '))
                if allocated_time < activity_lasts.total_seconds():
                    timestamp -= allocated_time

                    activity_lasts = timedelta(
                        0, round(timestamp - activities[-1][1])
                    )
                    input(
                        f'\nНовая продолжительность этапа: {CYAN}{activity_lasts}{WHITE}'
                    )

                else:
                    input(
                        f'\n{RED}Этап становится отрицательным, действие отменено{WHITE}'
                    )
            except BaseException as val:
                input(f'\n\n{RED}Действие отменено{WHITE}')

    # Add a note
    if session_id == len(ACTIVITIES) + 4:
        if not activities:
            input(stageline)
        else:
            activity_name = activities[-1][0]
            activity_start_time = activities[-1][2]
            activity_lasts = timedelta(0, round(timestamp - activities[-1][1]))

            print(
                f'Добавление подписи к предыдущему занятию\n{activity_name} ({activity_start_time}) {CYAN}{activity_lasts}{WHITE}'
            )
            note = input('\nПодпись: ')

            activities[-1][-1] = note

    if session_id == len(ACTIVITIES) + 5:
        if not activities:
            input(stageline)
        else:
            print('Вы уверены, что хотите удалить все занятия?')
            if input('y/n: ').lower() == 'y':
                clear_activities()
            else:
                input(f'\n{RED}Удаление отменено{WHITE}')

    data_save()
