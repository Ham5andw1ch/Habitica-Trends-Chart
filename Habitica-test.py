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
    if task["type"] == "daily":
        sorthistory = sorted(task["history"], key=lambda x: x["date"])
        tasks.append((task["text"], task["streak"], sorthistory))

# Empty set of dates included (needed for formatting later)
dates = set()
fig, ax = plt.subplots()
for task in tasks:

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
        line = ax.plot(x, y, "o", markersize=3, label=task[0])

        # If no points, just don't plot anything
        if len(x) > 0:
            z = numpy.polyfit(x, y, 1)
            p = numpy.poly1d(z)
            ax.plot(x, p(x), "--", color=line[0].get_color())
            dates.update(x)
    else:
        x = [int(point["date"]/1000 - (point["date"]/1000 % 86400))
             for point in task[2]]
        y = [point["value"] for point in task[2]]
        dates.update(x)

        # If no points, just don't plot anything
        if len(x) > 0:
            line = ax.plot(x, y, "o", markersize=3, label=task[0])
            z = numpy.polyfit(x, y, 1)
            p = numpy.poly1d(z)
            ax.plot(x, p(x), "--", color=line[0].get_color())

ax.legend()

ax.set_xticks(sorted(dates))
ax.set_xticklabels([stringDate(date) for date in sorted(dates)])
plt.xticks(rotation=-45)

plt.show()
