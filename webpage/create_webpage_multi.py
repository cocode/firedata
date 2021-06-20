from get_cal_fire_data import collect_data, get_annual_acres, summarize
import get_historical_data
import re, json
import io
# Run with python3 -m webpage.create_webpage_multi from firedata directory

# The webpage has several parts. The parts we care about
# The onLoad call back function, where we define charts
#   Within than, a definition for each chart
# The body
#   a defintion for an HTML div for each chart.

# Defintions of constant strings used to generate the page
head_preamble = \
"""
<head>
<meta charset="utf-8">
<style>
    .foot {font-size:50%; font-family: Verdana, sans-serif; margin-bottom: 0px; margin-top: 0px}
    .chart_target {width: 100%; }
    .chart_foot {margin-left: 100px; width: 100%}
    table, td, th {border-collapse: collapse; border: 1px solid blue}
    td, th {padding: 10px}
    th { background-color: #4488FF;}
    .sum_table {border-collapse: collapse; border: 10px solid blue}

</style>
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
"""

footer = \
"""    
<p class="foot">Source code: <a href="https://github.com/cocode/firedata">https://github.com/cocode/firedata</a></p>
<p class="foot">Data source: <a href="https://www.fire.ca.gov/incidents">https://www.fire.ca.gov/incidents</a></p>
<p class="foot">Accuracy not guaranteed</p>
"""
# Begins the onLoad function
begin_function = \
"""
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawCharts);
function drawCharts() {\n
"""

class Chart:
    def __init__(self, year, element, columns, options, footer=None):
        # TODO Chart data needs to be here, as well.
        self.element = element
        self.columns = columns
        self.options = options
        self.footer = footer
        self.chart_data = None # Loaded later

class WebPage:
    def __init__(self, year, charts):
        self.year = year
        self.subdir = "webpage"
        self.destination = F"{self.subdir}/fire_multi.html"
        self.acres_burned = None
        self.year_data = None
        self.charts = charts

    def load_historical_data(self):
        historical = get_historical_data.get_stats()
        return historical

    def load_calfire_year_data(self):
        """
        Loads the data from self.year. Also generates the summary info printed
        below the chart.
        :return:
        """
        summary = io.StringIO()
        START_JAN_ONE = False
        # Next three lines should be one function
        data_source = collect_data()
        acres_burned = get_annual_acres(data_source, year=self.year)
        self.sum_rows, self.sum_headers, self.sum_summary = summarize(data_source, year=self.year, output=summary)

        data_as_string = ""
        if START_JAN_ONE and len(acres_burned) > 0:
            if acres_burned[0][1] != 1 or acres_burned[0][2] != 1:
                data_as_string += F"[new Date({acres_burned[0][0]}, {1 - 1}, {1}), {0}],\n"

        for i in acres_burned:
            data_as_string += F"[new Date({i[0]}, {i[1] - 1}, {i[2]}), {i[3]}],\n"
        # print(data_as_string)
        self.year_data = data_as_string
        self.sum_str = summary.getvalue()

    def load(self):
        self.load_calfire_year_data()

    def write_chart_begin(self, output, chart):
        output.write('var data = new google.visualization.DataTable();\n')
        for column in chart.columns:
            output.write(F'data.addColumn("{column[0]}", "{column[1]}")\n');

    def write_chart_options(self, output, options):
        output.write("var options = ")
        output.write(json.dumps(options, indent=4))
        output.write("\n")

    def write_chart_data(self, output, chart):
        output.write("data.addRows([\n")
        year_data = chart.chart_data
        output.write(year_data)
        output.write("]);\n")

    def write_chart_end(self, output, chart):
        target = chart.element
        output.write(F'var chart = new google.visualization.ColumnChart(document.getElementById("{target}"))\n')
        output.write("chart.draw(data, options);\n")

    def write_chart(self, output, chart):
        target = chart.element
        self.write_chart_begin(output, chart)
        self.write_chart_options(output, chart.options)
        self.write_chart_data(output, chart)
        self.write_chart_end(output, chart)

    def write_onload_begin(self, output):
        """
        This starts the function that writes the javascript function called onLoad.
        :return:
        """
        output.write(begin_function)

    def write_onload_end(self, output):
        output.write("}\n")

    def write_onload_script(self, output):
        output.write('<script type="text/javascript">\n')
        self.write_onload_begin(output)
        for chart in self.charts:
            self.write_chart(output, chart)
        # self.write_chart(output, {'date': 'Season Start Date', 'number': 'Acres Burned'}, target )
        self.write_onload_end(output)
        output.write("</script>\n")

    def write_head(self, output):
        output.write(head_preamble)
        self.write_onload_script(output)
        output.write("</head>\n")

    def write_body_charts(self, output, chart):
        target = chart.element
        output.write(F'<div class="chart_target" id="{target}"></div>\n')
        if chart.footer:
            output.write('<div class="chart_foot">\n')
            output.write(chart.footer)
            output.write("\n</div>\n")
            output.write("<br>\n")

    def write_summary(self, output):
        # Temp hard code it.
        output.write('<p>Calfire: Change between last two data points (days):</p>')
        output.write('<table>\n')
        output.write("    <TR>\n")
        for col in self.sum_headers:
            output.write(F"        <th>{col}</td>\n")
        output.write("    </TR>\n")

        for row in self.sum_rows:
            output.write("    <TR>\n")
            for col in row:
                col = col.strip()
                if col and col[0] in "0123456789+-~" or col == "new":
                    align = "right" # Numeric column
                else:
                    align = "left"
                output.write(F"        <td style='text-align: {align};'>{col}</td>\n")
            output.write("    </TR>\n")
        output.write("</table>")
        output.write("<hr>")
        output.write('<p>Calfire: Active Incident Summary (days):</p>')

        output.write('<table>\n')
        output.write(F"        <th style='text-align:left;'>Cal Fire Stat</td>\n")
        output.write(F"        <th style='text-align:right;'>Value</td>\n")

        for row in self.sum_summary:
            alignment = ["left", "right"]
            assert len(row) == len(alignment)
            output.write("    <TR>\n")
            for col in range(len(row)):
                output.write(F"        <td style='text-align: {alignment[col]}; border: 1px solid black; padding: 10px'>{row[col]}</td>\n")
            output.write("    </TR>\n")
        output.write("</table>")

    def write_footer(self, output):
        output.write(footer)

    def write_body(self, output):
        output.write("<body>\n")
        output.write("<h1>California Fire Data</h1>")
        for chart in self.charts:
            self.write_body_charts(output, chart)
        output.write("<hr>\n")
        self.write_summary(output)
        output.write("<hr>\n")
        self.write_footer(output)
        output.write("</body>\n")

    def write_document(self, output):
        output.write("<!DOCTYPE html>\n<html>\n")
        self.write_head(output)
        self.write_body(output)
        output.write("</html>\n")

    def create(self):
        with open(self.destination, "w") as f:
            self.write_document(f)


if __name__ == "__main__":
    year = 2021


    with open("webpage/chart_calfire.json") as f:
        data_charts = json.load(f)
    chart_list = []
    for data_chart in data_charts:
        c = Chart(year, data_chart['element_id'], data_chart['columns'], data_chart['options'], data_chart['footer'])
        chart_list.append(c)


    page = WebPage(year, chart_list)
    page.load()
    hist = page.load_historical_data()
    print(hist)
    hist_string = ""
    for y in hist:
        acres = y[2]
        fed_acres = y[4]
        acres = acres.replace(",", "")
        fed_acres = fed_acres.replace(",", "")
        # Javascript counts months from 0-11, so december is 11
        hist_string += F'[new Date({y[0]}, 11, 31), {acres}, {fed_acres}],\n'
    print(hist_string)

    # TODO: Get the data from .json
    chart_list[0].chart_data = page.year_data
    chart_list[1].chart_data = hist_string
    page.create()

