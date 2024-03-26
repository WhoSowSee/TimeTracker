from datetime import datetime

import matplotlib.pyplot as plt
from matplotlib.patches import Patch

import save
from setup import setup
from utils import (
    create_graphics_directory_path,
    DAY,
    generate_activities_times,
    HOUR,
    MINUTE,
    normalize_color,
    WEEK,
)

ARGS, ACTIVITIES = setup("map")
activities_times = generate_activities_times(save.activities, save.timestamp)
GRAPH_NAME = 'map'

# Create plot canvas
fig, axs = plt.subplot_mosaic(
    [["main"]],
    figsize=(ARGS["PLOT_WIDTH"], ARGS["PLOT_HEIGHT"]),
)

fig.canvas.manager.set_window_title("Карта сохранения")
ax = list(axs.items())

all_experiment_time = sum([sum(activities_times[i]) for i in activities_times])
save_activities = set([i[0] for i in save.activities])

average_day = {
    activity_name: sum(activities_times[activity_name])
    for activity_name in ACTIVITIES
    if activity_name != ARGS["VOID"] and activity_name in save_activities
}


def bar_constructor(x, y):
    global offset

    if activity[0] != ARGS["VOID"]:
        ax[0][1].bar(
            x=x,
            bottom=offset,
            width=1,
            height=y,
            linewidth=0.5,
            color=normalize_color(ACTIVITIES[activity[0]]),
        )

    offset += y


# Generate all parts and add it to plot
experiment_start_time = save.activities[0][1]
offset = experiment_start_time % DAY + ARGS["UTC_OFFSET"]
days = 1

for activity in save.activities:
    # Create one bar
    if activities_times[activity[0]][0] <= DAY - offset:
        bar_constructor(days, activities_times[activity[0]][0])

    else:
        to_distribute = activities_times[activity[0]][0]
        to_distribute -= DAY - offset
        bar_constructor(days, DAY - offset)

        # Create bars, separated by days
        while to_distribute != 0:
            days += 1
            offset = 0

            if to_distribute >= DAY:
                bar_constructor(days, DAY)
                to_distribute -= DAY
            else:
                bar_constructor(days, to_distribute)
                to_distribute = 0

    activities_times[activity[0]].pop(0)

if ARGS["SHOW_LEGEND"]:
    legend_elements = [
        Patch(
            facecolor=normalize_color(ACTIVITIES[i]),
            edgecolor="black",
            linewidth=0.5,
            label=i,
        )
        for i in average_day
        if i != ARGS["VOID"]
    ]

    ax[0][1].legend(
        handles=legend_elements, ncol=ARGS["LEGEND_COLUMNS"], loc="lower left"
    )

start_day = datetime.fromtimestamp(save.activities[0][1]).weekday()
start_hour = experiment_start_time % (DAY) + ARGS["UTC_OFFSET"]

days_of_week = ("Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс")


def format_coord(x, y):
    x = int(x - 0.5)
    y = round(y / HOUR) if round(y / HOUR, 1) == round(y / HOUR) else round(y / HOUR, 1)

    selected_time = x * DAY + y * HOUR + experiment_start_time - start_hour

    # Form bar info
    bar_info = ""
    for k, i in enumerate(save.activities):
        if (
            i[1] >= selected_time
            or not save.activities[0][1] <= selected_time <= save.timestamp
        ):
            break
        pivot = (
            save.timestamp
            if len(save.activities) - 1 == k
            else save.activities[k + 1][1]
        )

        bar_info = f"{i[0]}"
        bar_info += f" ({i[-1]})" if i[-1] else ""
        bar_info += (
            f" ({round((pivot - i[1]) / HOUR, 1)}ч)\n"
            if (pivot - i[1]) / HOUR >= 1
            else f" ({round((pivot - i[1]) / MINUTE, 1)}м)\n"
        )

    # Form position info
    position_info = (
        f"x={days_of_week[(x + start_day) % 7]}, {y=}ч "
        f"({round((selected_time - experiment_start_time) // WEEK + 1)} неделя)"
    )

    return bar_info + position_info


ax[0][1].format_coord = format_coord

ax[0][1].set_xticks(
    range(1, days + 1, 7), [(i + start_day) for i in range(1, days + 1, 7)]
)
ax[0][1].set_xlim(0.5, days + 0.5)
ax[0][1].xaxis.set_major_formatter(lambda x, _: int(x - 0.5) // 7 + 1)

ax[0][1].set_yticks(
    range(0, DAY + 1, DAY // 10), [f"{i}%" for i in range(0, 101, 10)]
)
ax[0][1].set_ylim(0, DAY)
ax[0][1].yaxis.set_major_formatter(
    lambda y, _: f"{round(y / HOUR) if round(y / HOUR, 1) == round(y / HOUR) else round(y / HOUR, 1)}ч"
)

plt.tight_layout()
plt.savefig(create_graphics_directory_path(GRAPH_NAME), bbox_inches="tight")

if not ARGS["SILENT"]:
    plt.show()
