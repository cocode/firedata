"""
Simple program to generate a code coverage badge, using shields.io

A couple of notes: github seems to cache user content for a short while (maybe a minute?), so
don't be surprised if your changes take a bit to be visible.

WHY DOES THIS EXIST:
The examples on the main page of shields.io only work if you are using a supported service.
If you are running your own code coverage on github actions, then that won't work for you.

WHAT TO DO:
We are using the shields.io json api: https://shields.io/endpoint
To use it, we need to have a json blob put somewhere it can be reached from shields.io.
I check the into github, and then reference in your README.md file like this:

![Code Coverage](https://img.shields.io/endpoint?style=plastic&url=https%3A%2F%2Fraw.githubusercontent.com%2Fcocode%2Ffiredata%2Fmaster%2Fcode-coverage.txt)

You can use the json api page above to customize the URL for yourself.
Then, when you run your continuous integration job, take the percentage covered, and
run this program with the percentage as an argument:

    python make_badge 92

Then check the resulting page into github (or put it on s3, etc.)


"""
import json
import re
import sys

colors = {
    # Totally arbitrary values/colors. Pick your own.
    0: "red",
    25: "orange",
    50: "yellow",
    75: "green",
    95: "brightgreen",
    100: "#31c854" # Match other github badges "success" green.
}


def generate_response(percent):
    """
    Generate the response we will give to shields.io to get our badge.
    :param percent: The percentage of code coverage we have.
    :return: a dict.
    """
    for key in colors:
        if percent <= key:
            break

    color = colors[key]
    response = {
      "schemaVersion": 1,
      "label": "coverage",
      "message": F"{percent}%",
      "color": color
    }
    return response


def get_percentage():
    coverage_report_file = "coverage.txt"
    with open(coverage_report_file) as f:
            coverage_report = f.readlines()
    last_line = coverage_report[-1]
    match = re.search(r'[0-9]+%', last_line)
    p = int(match.group(0)[:-1])
    return p

def run():
    p = get_percentage()
    response = generate_response(p)
    with open("code-coverage.txt", "w") as f:
        f.write(json.dumps(response, indent=4))


if __name__ == "__main__":
    run()