from get_cal_fire_data import collect_data, get_annual_acres, summarize
import re, json
import io


def load_html(source):
    with open(source) as f:
        html = f.read()
    return html


def replace_data(html:str, data, year:int, summary:str):
    """
    Using a template file, generate a web page with chart(s) and information.
    :param html: The HTML template to use
    :param data: Data used to generate the chart
    :param year: The year to display
    :param summary: The summary text
    :return: The finished webpage
    """
    html = html.replace("Company Performance", "Fire Data")
    html = html.replace("{{YEAR}}", str(year))
    if type(data) == str:
        replacement = data
    else:
        replacement = json.dumps(data, indent=4)
    html = re.sub("DATA_GOES_HERE", replacement, html, flags=re.MULTILINE)
    html = re.sub("{{SUMMARY}}", "<pre>"+summary+"</pre>", html, flags=re.MULTILINE)
    return html


def write_html(html, destination):
    print("Writing: ", destination)

    with open(destination, "w") as f:
        f.write(html)

    print("Wrote..: ", destination)


if __name__ == "__main__":
    year = 2021

    subdir = "webpage"
    summary = io.StringIO()
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
    acres_burned = get_annual_acres(data_source, year=year)
    summarize(data_source, year=year, output=summary)


    data_as_string = ""
    if START_JAN_ONE and len(acres_burned) > 0:
        if acres_burned[0][1] != 1 or acres_burned[0][2] != 1:
            data_as_string += F"[new Date({acres_burned[0][0]}, {1 - 1}, {1}), {0}],\n"

    for i in acres_burned:
        data_as_string += F"[new Date({i[0]}, {i[1]-1}, {i[2]}), {i[3]}],\n"
    #print(data_as_string)
    data = data_as_string
    sum_str = summary.getvalue()
    html = replace_data(html, data, year, sum_str)
    write_html(html, destination)