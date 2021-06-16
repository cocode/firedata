from get_cal_fire_data import collect_data, get_annual_acres
import re, json


def load_html(source):
    with open(source) as f:
        html = f.read()
    return html


def replace_data(html:str, data):
    html = html.replace("Company Performance", "Fire Data") # TODO Year
    if type(data) == str:
        replacement = data
    else:
        replacement = json.dumps(data, indent=4)
    print(replacement)
    html = re.sub("DATA_GOES_HERE", replacement, html, flags=re.MULTILINE)
    return html


def write_html(html, destination):
    print("Writing: ", destination)

    with open(destination, "w") as f:
        f.write(html)

    print("Wrote..: ", destination)


if __name__ == "__main__":
    subdir = "webpage"
    BAR = True
    START_JAN_ONE = False
    if BAR:
        source = F"{subdir}/template_bar_graph.html"
    else:
        source = F"{subdir}/template_   line_graph.html"

    destination = F"{subdir}/fire_graphs.html"
    assert(source != destination)
    html = load_html(source)
    # Next three lines should be one function
    data_source = collect_data()
    #ydata, tdata, incidents = get_data(data_source, 2021)
    acres_burned = get_annual_acres(data_source)

    if True:
        data_as_string = ""
        if START_JAN_ONE and len(acres_burned) > 0:
            if acres_burned[0][1] != 1 or acres_burned[0][2] != 1:
                data_as_string += F"[new Date({acres_burned[0][0]}, {1 - 1}, {1}), {0}],\n"

        for i in acres_burned:
            data_as_string += F"[new Date({i[0]}, {i[1]-1}, {i[2]}), {i[3]}],\n"
        print(data_as_string)
        data = data_as_string
    else:
        data = [
              ['Year', 'Sales', 'Expenses'],
              ['2004',  1000,      400],
              ['2005',  1170,      460],
              ['2006',  660,       1120],
              ['2007',  1030,      540]
            ]
    html = replace_data(html, data)
    write_html(html, destination)