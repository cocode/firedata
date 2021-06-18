"""
This file returns fire data from the last 32 years (up to 2018)

This file reads the mangled data sourced from the "fires-acres-all-agencies-thru-2018.pdf".
Copying from that file produces one single run of numbers with no spaces, so I then
converted to .doc  (https://pdf2doc.com/), and then copied and pasted into the text file.
But the text file was one number per line, so this file concatenates it back into its original
rows and columns.

Columns are
year
CAL FIRE - Fires
CAL FIRE - Acres
Federal Firefighting Agencies - Fires
Federal Firefighting Agencies - Acres
Local Government* - Fires
Local Government* - Acres
TOTAL - Fires
TOTAL - Acres
"""
import json

source_file_name = "data/data_cal_annual/fires-acres-all-agencies-thru-2018.txt"
output_file_name = "data/data_cal_annual/fires-acres-all-agencies-thru-2018-rows.txt"


def get_stats():
    """
    Reads and returns the stored historical data.

    :return: List of rows of columns. See above for details.
    """
    with open(output_file_name) as f:
        rows = json.load(f)
    return rows


def _get_source_data():
    """
    Finishes converting the data we got from the source PDF, into json.
    :return:
    """
    with open(source_file_name) as f:
        lines = f.readlines()

    columns = []
    rows = []
    for line in lines:
        columns.append(line.strip())
        if len(columns) == 13:
            rows.append(columns)
            columns = []

    if len(columns):
        rows.append(columns)

    for i in range(len(rows)):
        rows[i] = rows[i][0:2] + rows[i][3:9] + rows[i][10:11]
    return rows


def _write_converted_data():
    with open(output_file_name, "w") as f:
        f.write(json.dumps(rows, indent=4))


if __name__ == "__main__":
    rows = _get_source_data()
    _write_converted_data()
    rows = get_stats()
    print(rows)
