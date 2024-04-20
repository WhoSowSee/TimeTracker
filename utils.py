import os
from datetime import datetime

# Time
SECOND = 1
MINUTE = 60 * SECOND
HOUR = 60 * MINUTE
DAY = 24 * HOUR
WEEK = 7 * DAY

# Colors
WHITE = "\033[0m"
RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
BLUE = "\033[34m"
MAGENTA = "\033[35m"
CYAN = "\033[36m"

# Days
WEEKDAYS = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")

MONTHS = (
    "Января",
    "Февраля",
    "Марта",
    "Апреля",
    "Мая",
    "Июня",
    "Июля",
    "Августа",
    "Сентября",
    "Октября",
    "Ноября",
    "Декабря",
)


def normalize_color(activity):
    color = tuple([rgb / 255 for rgb in activity])

    return color


def generate_activities_times(activities, timestamp):
    save_activities_names = set([i[0] for i in activities])
    activities_times = {
        activity_name: [] for activity_name in save_activities_names
    }

    for i, activity in enumerate(activities):
        pivot = activities[i + 1][1] if i < len(activities) - 1 else timestamp
        activity_time = pivot - activity[1]

        # print(timedelta(activity_time))
        activities_times[activity[0]].append(activity_time)

    return activities_times


# Уже есть в tracker, но можно импортировать в tracker отсюда
# def stages_formatter(stages, verb=0) -> str:
#     if verb:
#         form = ["этапа", "этапов", "этапов"]
#     else:
#         form = ["этап", "этапа", "этапов"]

#     last_digit = int(str(stages)[-1])
#     last_2_digits = int(str(stages)[-2:])

#     if last_digit == 1 and last_2_digits != 11:
#         return f"{stages} {form[0]}"

#     if 1 <= last_digit <= 4 and (last_2_digits < 10 or last_2_digits > 20):
#         return f"{stages} {form[1]}"

#     return f"{stages} {form[2]}"


# def delta(time, cap=DAY):
#     for postfix, name in ((WEEK, 'н'), (DAY, 'д'), (HOUR, 'ч'), (MINUTE, 'м'), (SECOND, 'с')):
#         if time >= postfix and postfix <= cap:
#             time = time / postfix
#             return f"{round(time) if round(time, 1) == round(time) else round(time, 1)}{name}"


def timedelta(time) -> str:
    time = int(time)

    if time < DAY:
        weeks = ""
    else:
        weeks = f"{time // DAY}д"
        time -= DAY * (time // DAY)

        if time == 0:
            return weeks
        else:
            weeks += " "

    clock = []
    for period in (HOUR, MINUTE, SECOND):
        clock.append(f"{time // period:02}")
        time -= period * (time // period)

    return weeks + ':'.join(clock)


# Graphs path
def create_graphics_directory_path(graph_name: str) -> str:
    current_time = datetime.now().strftime("%d.%m.%Y.%H_%M")
    directory_images = 'graph_images'

    if not os.path.exists(directory_images):
        os.makedirs(directory_images)

    directory_path = os.path.join(
        directory_images, f"{graph_name}{current_time}.png"
    )

    return directory_path
