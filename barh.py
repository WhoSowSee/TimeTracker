import sys
from datetime import datetime
from math import ceil

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib.ticker import MultipleLocator, PercentFormatter

import save
from setup import setup
from utils import (
    DAY,
    HOUR,
    MINUTE,
    MONTHS,
    WEEK,
    WEEKDAYS,
    create_graphics_directory_path,
    generate_activities_times,
    normalize_color,
)

GRAPH_NAME = 'barh'
ARGS, ACTIVITIES = setup("barh")
activities_times = generate_activities_times(save.activities, save.timestamp)


save_activities = set([i[0] for i in save.activities])
average_day = {
    activity_name: sum(activities_times[activity_name])
    for activity_name in ACTIVITIES
    if activity_name in save_activities
}

# Create plot canvas
fig, axs = plt.subplot_mosaic(
    (["main"], ["average"]),
    figsize=(ARGS["PLOT_WIDTH"], ARGS["PLOT_HEIGHT"]),
    gridspec_kw={"height_ratios": (14, 1)},
)

fig.canvas.manager.set_window_title("Распределение времени")
ax = list(axs.items())


# First plot - bars for each days
def bar_constructor(x, y):
    global offset

    if activity[0] != ARGS["VOID"]:
        ax[0][1].barh(
            left=offset,
            y=y,
            width=x,
            height=1,
            edgecolor="black",
            linewidth=0.5,
            color=normalize_color(ACTIVITIES[activity[0]]),
        )

        if x >= DAY * ARGS["LABEL_THRESHOLD"]:
            ax[0][1].text(
                x=x / 2 + offset,
                y=y,
                s=f"{round(x / HOUR) if round(x / HOUR, 1) == round(x / HOUR) else round(x / HOUR, 1)}ч",
                va="center",
                ha="center",
                clip_on=True,
            )

    offset += x


# Generate all parts and add it to plot
experiment_start_time = save.activities[0][1]
all_experiment_time = save.timestamp - experiment_start_time

offset = experiment_start_time % DAY + ARGS["UTC_OFFSET"]
days = 1

for activity in save.activities:
    # Create one bar
    if activities_times[activity[0]][0] <= DAY - offset:
        bar_constructor(activities_times[activity[0]][0], days)

    else:
        to_distribute = activities_times[activity[0]][0]
        to_distribute -= DAY - offset
        bar_constructor(DAY - offset, days)

        # Create bars, separated by days
        while to_distribute != 0:
            days += 1
            # offset = 0
            offset -= DAY

            if to_distribute >= DAY:
                bar_constructor(DAY, days)
                to_distribute -= DAY
            else:
                bar_constructor(to_distribute, days)
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
        handles=legend_elements, ncol=ARGS["LEGEND_COLUMNS"], loc="upper left"
    )

start_day = datetime.fromtimestamp(save.activities[0][1]).weekday()
start_hour = experiment_start_time % DAY + ARGS["UTC_OFFSET"]


def format_coord(x, y):
    position_info = ""
    x = (
        round(x / HOUR)
        if round(x / HOUR, 1) == round(x / HOUR)
        else round(x / HOUR, 1)
    )
    y = int(y - 0.5)

    selected_time = y * DAY + x * HOUR + experiment_start_time - start_hour

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
        month = MONTHS[datetime.fromtimestamp(selected_time).month - 1]
        day = datetime.fromtimestamp(selected_time).day
        week = round((selected_time - experiment_start_time) // WEEK + 1)

        position_info = (
            f"{x=}ч, y={WEEKDAYS[(y+start_day)%7]} "
            f"({day} {month}, {week} неделя)"
        )
    return bar_info + position_info


view_shift = (
    ceil((all_experiment_time + start_hour) // DAY) - 13.5
    if ceil(all_experiment_time / WEEK) > 2
    else 0.5
)

ax[0][1].format_coord = format_coord

ax[0][1].set_xticks(
    range(0, DAY + 1, DAY // 10), [f"{i}%" for i in range(0, 101, 10)]
)
ax[0][1].set_xlim(0, DAY)
ax[0][1].xaxis.set_major_formatter(
    lambda x, _: f"{round(x / HOUR) if round(x / HOUR, 1) == round(x / HOUR) else round(x / HOUR, 1)}ч"
)

ax[0][1].set_yticks(
    range(1, days + 1),
    [WEEKDAYS[(i + start_day) % 7] for i in range(days)],
)
ax[0][1].set_ylim(view_shift, 15 + view_shift)
ax[0][1].invert_yaxis()
ax[0][1].yaxis.set_major_formatter(
    lambda y, _: WEEKDAYS[(int(y - 0.5) + start_day) % 7]
)

# Second plot - average time
offset = 0

for activity in average_day:
    if activity != ARGS["VOID"]:
        ax[1][1].barh(
            left=offset,
            y=1,
            width=average_day[activity],
            height=1,
            edgecolor="black",
            color=normalize_color(ACTIVITIES[activity]),
            linewidth=0.5,
        )

        if (
            average_day[activity]
            >= all_experiment_time * ARGS["AV_LABEL_THRESHOLD"]
        ):
            ax[1][1].text(
                y=1,
                x=(average_day[activity] / 2 + offset),
                s=f"{round(average_day[activity] / all_experiment_time * 100, 1)}%",
                va="center",
                ha="center",
                clip_on=True,
            )

    offset += average_day[activity]


def format_coord(x, y):
    time_offset = 0

    # Form bar info
    bar_info = ""
    for activity in average_day:
        if time_offset + average_day[activity] > x:
            bar_info = f"{activity} ({round(average_day[activity] / all_experiment_time * 100, 1)}%)\n"
            break

        time_offset += average_day[activity]

    # Form position info
    position_info = f"x={round(x / all_experiment_time * 100, 1)}%, y=AV"

    return bar_info + position_info


average_time_max = all_experiment_time - (
    average_day[ARGS["VOID"]] if ARGS["HIDE_VOID"] else 0
)

ax[1][1].format_coord = format_coord

ax[1][1].set_xlim(0, average_time_max)
ax[1][1].xaxis.set_major_formatter(PercentFormatter(all_experiment_time))
ax[1][1].xaxis.set_major_locator(MultipleLocator(average_time_max / 10))

ax[1][1].set_yticks((1,), ("AV",))
ax[1][1].set_ylim(0.5, 1.5)
ax[1][1].yaxis.set_major_formatter(lambda *_: "AV")

plt.tight_layout()
plt.savefig(create_graphics_directory_path(GRAPH_NAME), bbox_inches="tight")

if not ARGS["SILENT"]:
    plt.show()
