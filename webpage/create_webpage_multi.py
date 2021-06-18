from get_cal_fire_data import collect_data, get_annual_acres, summarize
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
<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
"""

footer = \
"""    
<p style="font-size:50%; font-family: Verdana, sans-serif; margin-bottom: 0px; margin-top: 0px">Source code: <a href="https://github.com/cocode/firedata">https://github.com/cocode/firedata</a></p>
<p style="font-size:50%; font-family: Verdana, sans-serif; margin-bottom: 0px; margin-top: 0px">Data source: <a href="https://www.fire.ca.gov/incidents">https://www.fire.ca.gov/incidents</a></p>
<p style="font-size:50%; font-family: Verdana, sans-serif; margin-bottom: 0px; margin-top: 0px">Accuracy not guaranteed</p>
"""
# Begins the onLoad function
begin_function = \
"""
google.charts.load('current', {'packages':['corechart']});
google.charts.setOnLoadCallback(drawCharts);
function drawCharts() {\n
"""


class WebPage:
    def __init__(self, year):
        self.year = year
        self.subdir = "webpage"
        self.destination = F"{self.subdir}/fire_multi.html"
        self.acres_burned = None
        self.year_data = None

    def load_year_data(self):
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
        summarize(data_source, year=self.year, output=summary)

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
        self.load_year_data()

    def write_chart_begin(self, output, columns):
            output.write('var data = new google.visualization.DataTable();\n')
            for key in columns:
                output.write(F'data.addColumn("{key}", "{columns[key]}")\n');

    def write_chart_options(self, output, title, haxis, vaxis):
        options = {}
        options["title"] = title
        options["hAxis"] = {"title":haxis}
        options["vAxis"] = {"title":vaxis}
        output.write("var options = ")
        output.write(json.dumps(options, indent=4))
        output.write("\n")

    def write_chart_data(self, output):
        output.write("data.addRows([\n")

        output.write(self.year_data)
        output.write("]);\n")

    def write_chart_end(self, output, target):
        output.write(F'var chart = new google.visualization.ColumnChart(document.getElementById("{target}"))\n')
        output.write("chart.draw(data, options);\n")

    def write_chart(self, output, columns, target):
        self.write_chart_begin(output, columns)
        self.write_chart_options(output,
                                 F'Cal Fire Wildfire Data {self.year}',
                                 F'Date Recorded',
                                 F'Cumulative Acres Burned')
        self.write_chart_data(output)
        self.write_chart_end(output, target)

    def write_onload_begin(self, output):
        """
        This starts the function that writes the javascript function called onLoad.
        :return:
        """
        output.write(begin_function)

    def write_onload_end(self, output):
        output.write("}\n")

    def write_onload_script(self, output, target):
        output.write('<script type="text/javascript">\n')
        self.write_onload_begin(output)
        self.write_chart(output, {'date': 'Season Start Date', 'number': 'Acres Burned'}, target )
        self.write_onload_end(output)
        output.write("</script>\n")

    def write_head(self, output, target):
        output.write(head_preamble)
        self.write_onload_script(output, target)
        output.write("</head>\n")

    def write_body_charts(self, output, target):
        output.write(F'<div id="{target}" style="width: 900px; height: 500px"></div>\n')

    def write_summary(self, output):
        # Temp hard code it.
        output.write("<pre>\n")
        output.write("Change between last two data points (days):\n")
        output.write(self.sum_str)
        output.write("</pre>\n")

    def write_footer(self, output):
        output.write(footer)

    def write_body(self, output, target):
        output.write("<body>\n")
        self.write_body_charts(output, target)
        output.write("<hr>\n")
        self.write_summary(output)
        output.write("<hr>\n")
        self.write_footer(output)
        output.write("</body>\n")

    def write_document(self, output):
        output.write("<!DOCTYPE html>\n<html>\n")
        target = "acres_chart"
        self.write_head(output, target)
        self.write_body(output, target)
        output.write("</html>\n")

    def create(self):
        self.load()
        with open(page.destination, "w") as f:
            page.write_document(f)


if __name__ == "__main__":
    page = WebPage(2021)
    page.create()

