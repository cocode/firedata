"""
When run from the command line, this file converts data pulled from the calfire 2018 redbook, and other sources,
and writes it to a file. This only needs to be done once, then the results are checked in to git.

When get_stats() is called, it returns the contents of the above file.

The data contains fire data from the last 32 years (up to 2018), plus two years of data from other sources.

This file reads the mangled data sourced from the "fires-acres-all-agencies-thru-2018.pdf".
Just copy/pasting from that file produces one single run of numbers with no spaces, so I instead
converted to .doc  (https://pdf2doc.com/), and then copied and pasted that into a text file.
That left the text file with one number per line, so this file concatenates it back into its original
rows and columns, and saves it.

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
    Reads and returns the stored historical data for calfire
     source: https://www.fire.ca.gov/media/iy1gpp2s/2019_redbook_final.pdf

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
    # Don't have official numbers for local agencies for 2019. Use zero for now.
    row = [str(2019), str(cf_2019_fires), str(cf_2019_acres), str(fed_2019_fires), str(fed_2019_acres), "0", "0",
           str(total_fires), str(total_acres)]
    print(row)
    return row

def get_2020_data():
    """
    Add data from 2020 to the historical table. The 2020 Redbook is not out yet, so source the
    calfire state data https://www.fire.ca.gov/stats-events/:
    "January 1, 2020 through December 29, 2020 	8,112 	1,443,152"
    "2020 Combined YTD (CALFIRE & Federal) 	9,917 	4,257,863"

    :return:
    """
    cf_2020_fires = 8112
    cf_2020_acres = 1443152
    total_fires = 9917
    total_acres = 4257863
    fed_2020_fires = total_fires - cf_2020_fires
    fed_2020_acres = total_acres - cf_2020_acres

    # Don't have official numbers for local agencies for 2019. Use zero for now.
    row = [str(2020), str(cf_2020_fires), str(cf_2020_acres), str(fed_2020_fires), str(fed_2020_acres), "0", "0",
           str(total_fires), str(total_acres)]
    print(row)
    return row

def get_fed_history():
    """
    Return the US fire historical data sourced from: https://www.nifc.gov/fire-information/statistics/wildfires
    :return:
    """
    data = [
        ('1983', '18229', '1323666'),
        ('1984', '20493', '1148409'),
        ('1985', '82591', '2896147'),
        ('1986', '85907', '2719162'),
        ('1987', '71300', '2447296'),
        ('1988', '72750', '5009290'),
        ('1989', '48949', '1827310'),
        ('1990', '66481', '4621621'),
        ('1991', '75754', '2953578'),
        ('1992', '87394', '2069929'),
        ('1993', '58810', '1797574'),
        ('1994', '79107', '4073579'),
        ('1995', '82234', '1840546'),
        ('1996', '96363', '6065998'),
        ('1997', '66196', '2856959'),
        ('1998', '81043', '1329704'),
        ('1999', '92487', '5626093'),
        ('2000', '92250', '7393493'),
        ('2001', '84079', '3570911'),
        ('2002', '73457', '7184712'),
        ('2003', '63629', '3960842'),
        ('2004', '65461', '8097880'),
        ('2005', '66753', '8689389'),
        ('2006', '96385', '9873745'),
        ('2007', '85705', '9328045'),
        ('2008', '78979', '5292468'),
        ('2009', '78792', '5921786'),
        ('2010', '71971', '3422724'),
        ('2011', '74126', '8711367'),
        ('2012', '67774', '9326238'),
        ('2013', '47579', '4319546'),
        ('2014', '63312', '3595613'),
        ('2015', '68151', '10125149'),
        ('2016', '67743', '5509995'),
        ('2017', '71499', '10026086'),
        ('2018', '58083', '8767492'),
        ('2019', '50477', '4664364'),
        ('2020', '58950', '10122336'),
    ]
    return data


def run():
    rows = _get_source_data()
    d2019 = get_2019_data()
    rows.append(d2019)

    d2020 = get_2020_data()
    rows.append(d2020)

    _write_converted_data(rows)

if __name__ == "__main__":
    run()  # pragma: no cover

