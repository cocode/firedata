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
output_file_name = "data/data_cal_annual/fires-acres-all-agencies-thru-2018.json"


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


def _write_converted_data(row_data):
    with open(output_file_name, "w") as f:
        f.write(json.dumps(rows, indent=4))

def get_2019_data():
    """
    Add data from 2019 to the historical table. The are in different formats, so we
    have to adjust a bit.
    :return:
    """
    with open("data/data_cal_annual/2019-redbook-table-1.txt") as f:
        table = json.load(f)
    print(json.dumps(table, indent=4))
    cf_2019_fires = table[0][1] + table[1][1]
    cf_2019_acres = table[0][2] + table[1][2]
    fed_2019_fires = table[3][1] + table[4][1]  + table[5][1] + table[6][1] + table[7][1] + table[8][1]
    fed_2019_acres = table[3][2] + table[4][2]  + table[5][2] + table[6][2] + table[7][2] + table[8][2]
    total_fires = cf_2019_fires + fed_2019_fires
    total_acres = cf_2019_acres + fed_2019_acres
    row = [str(2019), str(cf_2019_fires), str(cf_2019_acres), str(fed_2019_fires), str(fed_2019_acres), "N/A", "N/A",
           str(total_fires), str(total_acres)]
    print(row)
    return row


if __name__ == "__main__":
    rows = _get_source_data()
    d2019 = get_2019_data()
    rows.append(d2019)
    _write_converted_data(rows)

    rows = get_stats()
    #print(rows)
    get_2019_data()


