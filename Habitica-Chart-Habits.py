#!/usr/bin/python3

import urllib.request
import json
import datetime
import numpy
import matplotlib.pyplot as plt
import sys

# Helper Functions


def stringDate(dateint):
    return datetime.date.fromtimestamp(dateint).strftime("%Y-%m-%d")


def habiticaDateToEpoch(dateint):
    return int(dateint/1000-(dateint/1000 % 86400))


user_token = ""
api_token = ""

if len(sys.argv) < 3:
    print("Syntax: Habitica-test.py user-token api-token [numberOfDaysBack]")
    sys.exit(0)
else:
    user_token = sys.argv[1]
    api_token = sys.argv[2]

# Get the user's tasks
request = urllib.request.Request("https://habitica.com/api/v3/tasks/user")
request.add_header('x-api-user', user_token)
request.add_header('x-api-key', api_token)

contents = urllib.request.urlopen(request).read()

tasks = []

obj = json.loads(contents)

# Add the tasks to a list
for task in obj["data"]:
    if task["type"] == "daily" or task["type"] == "habit":
        sorthistory = sorted(task["history"], key=lambda x: x["date"])
        # tasks.append((task["text"], task["streak"], sorthistory))
        tasks.append((task["text"], task["type"], sorthistory))

# Empty set of dates included (needed for formatting later)
dates = {}
fig, ax = plt.subplots(1, 2, constrained_layout=True)
for task in tasks:
    axis = 0
    if task[1] == "daily":
        axis = 0
    elif task[1] == "habit":
        axis = 1

    # If we have a forth argument, use it as a cutoff range
    if len(sys.argv) == 4:
        cutoff = (datetime.datetime.now().timestamp() -
                  datetime.datetime.now().timestamp() % 86400) - \
                 (86400 * int(sys.argv[3]))

        # Fancy list comprehensions to cutoff dates
        x = [habiticaDateToEpoch(point["date"]) for point in task[2] if
             (habiticaDateToEpoch(point["date"]) > cutoff)]
        y = [point["value"] for point in task[2] if
             (habiticaDateToEpoch(point["date"]) > cutoff)]

        # If no points, just don't plot anything
        if len(x) > 0:
            line = ax[axis].plot(x, y, "o", markersize=3, label=task[0])
            z = numpy.polyfit(x, y, 1)
            p = numpy.poly1d(z)
            ax[axis].plot(x, p(x), "--", color=line[0].get_color())
            if axis not in dates:
                dates[axis] = set()
            dates[axis].update(x)
    else:
        x = [int(point["date"]/1000 - (point["date"]/1000 % 86400))
             for point in task[2]]
        y = [point["value"] for point in task[2]]

        # If no points, just don't plot anything
        if len(x) > 0:
            line = ax[axis].plot(x, y, "o", markersize=3, label=task[0])
            z = numpy.polyfit(x, y, 1)
            p = numpy.poly1d(z)
            ax[axis].plot(x, p(x), "--", color=line[0].get_color())
            if axis not in dates:
                dates[axis] = set()
            dates[axis].update(x)

for axis in range(0, len(ax)):
    ax[axis].set_ylabel("Value")
    ax[axis].set_xlabel("Date")
    if axis in dates:
        ax[axis].legend()
        ax[axis].set_xticks(sorted(dates[axis]))
        ax[axis].tick_params(rotation=-45)
        ax[axis].set_xticklabels([stringDate(date) for
                                 date in sorted(dates[axis])])
    else:
        fig.delaxes(ax[axis])

ax[0].set_title("Dailies")
ax[1].set_title("Habits")
plt.show()
