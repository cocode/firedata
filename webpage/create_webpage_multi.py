from get_cal_fire_data import collect_data, get_annual_acres, summarize
import re, json
import io
# Run with python3 -m webpage.create_webpage_multi from firedata directory


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

    def write_script(self, output):
        output.write('        <script type="text/javascript">\n')
        function_part1 = \
    """            google.charts.load('current', {'packages':['corechart']});
              google.charts.setOnLoadCallback(drawCharts);
        
              function drawCharts() {
                var data = new google.visualization.DataTable();
                data.addColumn('date', 'Season Start Date');
                data.addColumn('number', 'Acres Burned');
                data.addRows([
"""
        function_part2 = \
"""              var options = {
                  title: 'Cal Fire Wildfire Data {{YEAR}}',
        
                hAxis: {
                  title: 'Date Recorded',
                },
                vAxis: {
                  title: 'Cumulative Acres Burned'
                }
              };
        
                var chart = new google.visualization.ColumnChart(document.getElementById('acres_chart'))
                chart.draw(data, options);
              }
"""
        output.write(function_part1)
        output.write(self.year_data)
        output.write("]);\n")
        output.write(function_part2)
        output.write("        </script>\n")

    def write_head(self, output):
        preamble = \
"""    <head>
        <meta charset="utf-8">
        <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
"""
        output.write(preamble)
        self.write_script(output)
        output.write("    </head>\n")

    def write_body_charts(self, output):
        output.write('        <div id="acres_chart" style="width: 900px; height: 500px"></div>\n')

    def write_summary(self, output):
        # Temp hard code it.
        output.write("<pre>\n")
        output.write("Change between last two data points (days):\n")
        output.write(self.sum_str)
        output.write("</pre>\n")

    def write_footer(self, output):
        footer = \
"""    <p style="font-size:50%; font-family: Verdana, sans-serif; margin-bottom: 0px; margin-top: 0px">Source code: <a href="https://github.com/cocode/firedata">https://github.com/cocode/firedata</a></p>
    <p style="font-size:50%; font-family: Verdana, sans-serif; margin-bottom: 0px; margin-top: 0px">Data source: <a href="https://www.fire.ca.gov/incidents">https://www.fire.ca.gov/incidents</a></p>
    <p style="font-size:50%; font-family: Verdana, sans-serif; margin-bottom: 0px; margin-top: 0px">Accuracy not guaranteed</p>
"""
        output.write(footer)

    def write_body(self, output):
        output.write("    <body>\n")
        self.write_body_charts(output)
        output.write("    <hr>\n")
        self.write_summary(output)
        output.write("    <hr>\n")
        self.write_footer(output)
        output.write("    </body>\n")

    def write_document(self, output):
        output.write("<!DOCTYPE html>\n<html>\n")
        self.write_head(output)
        self.write_body(output)
        output.write("</html>\n")

    def create(self):
        self.load()
        with open(page.destination, "w") as f:
            page.write_document(f)


if __name__ == "__main__":
    page = WebPage(2021)
    page.create()

