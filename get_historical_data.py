"""
This file returns fire data from the last 32 years (up to 2018)

This file reads the mangled data from the "fires-acres-all-agencies-thru-2018.pdf", which I then
converted to .doc  (https://pdf2doc.com/), and then copied and pasted into the text file. But the text file
was one number per line, this file concatenates it back into its original rows and columns.

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

def get_stats():
    with open("data/data_cal_annual/fires-acres-all-agencies-thru-2018.txt") as f:
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

if __name__ == "__main__":
    rows = get_stats()
    for row in rows:
        print(row)