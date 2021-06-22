import datetime

import get_cal_fire_data
import json
from webpage.analyzers import AnalyzerUs, AnalyzerUsCa, AnalyzerCalFire, AnalyzerCaHistorical
# Run with python3 -m webpage.create_webpage_multi from firedata directory

# The webpage has several parts. The parts we care about
# The onLoad call back function, where we define charts
#   Within than, a definition for each chart
# The body
#   a defintion for an HTML div for each chart.

# Definitions of constant strings used to generate the page
head_preamble = \
"""
<head>
<meta charset="utf-8">
<style>
    .introduction {margin-left: 100px; margin-right: 100px;}
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
    def __init__(self, year, element, columns, options, footer=None, analyzer=None):
        self.element = element
        self.columns = columns
        self.options = options
        self.footer = footer
        self.analyzer_name = analyzer
        self.analyzer = globals()[analyzer]()  # type('TempAnalyzer', (self.analyzer_name,), {})
        self.chart_data = None


class WebPage:
    def __init__(self, year, charts):
        self.year: int = year
        self.acres_burned = None
        self.year_data = None
        self.charts = charts

    def load_table_data(self):
        # Load table data
        data_source = get_cal_fire_data.get_data_store()
        self.sum_rows, self.sum_headers, self.sum_summary, ignored = get_cal_fire_data.summarize(data_source, year=self.year)

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
        output.write("    <tr>\n")
        for col in self.sum_headers:
            output.write(F"        <th>{col}</th>\n")
        output.write("    </tr>\n")

        for row in self.sum_rows:
            output.write("    <tr>\n")
            for col in row:
                col = col.strip()
                if col and col[0] in "0123456789+-~" or col == "new":
                    align = "right" # Numeric column
                else:
                    align = "left"
                output.write(F"        <td style='text-align: {align};'>{col}</td>\n")
            output.write("    </tr>\n")
        output.write("</table>")
        output.write("<hr>")
        output.write('<p>Calfire: Active Incident Summary (days):</p>')

        output.write('<table>\n')
        output.write("    <tr>\n")
        output.write(F"        <th style='text-align:left'>Cal Fire Stat</th>\n")
        output.write(F"        <th style='text-align:right;'>Value</th>\n")

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
        """onclick="window.open(document.URL, '_blank', 'location=yes,height=570,width=520,scrollbars=yes,status=yes');">"""
        output.write("""
            <span style="float:right; margin-right:100;">
            <select onchange="alert('Not implemented')" name="cars" id="cars">
                <option selected="selected" value="fire_2019.html">California</option>
                <option value="fire_2020.html">Washington</option>
            </select>
        """)
        output.write('<select onchange="window.location=this.options[this.selectedIndex].value;" name="year" id="year">\n')
        for i in range(2021, 2018, -1):
            attr = 'selected="selected"' if self.year == i else ""
            output.write(F'<option {attr} value="fire_{i}.html">{i}</option>\n')
        output.write('</select></span>\n');

        output.write("<h1>California Fire Data</h1>")
        output.write('<p class="introduction">This site attempts to visualize California fire data.</p>')
        output.write('<p class="introduction">Fires in california may be fought by Federal agencies, California State agencies ("Cal Fire"), ')
        output.write(' or local agencies, and the reporting is different for all. </p>')
        for chart in self.charts:
            self.write_body_charts(output, chart)
        this_year = datetime.date.today().year
        if self.year == this_year:
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

    def create(self, destination: str):
        with open(destination, "w") as f:
            self.write_document(f)


def create_webpage(destination: str, year: int, x_min_date: datetime.date= None):
    with open("webpage/chart_calfire.json") as f:
        data_charts = json.load(f)
    chart_list = []
    for data_chart in data_charts:
        c = Chart(year, data_chart['element_id'], data_chart['columns'], data_chart['options'], data_chart['footer'],
                  data_chart['analyzer'])
        chart_list.append(c)

    page = WebPage(year, chart_list)
    for chart in chart_list:
        data = chart.analyzer.get_data(year, x_min_date=x_min_date)
        chart.chart_data = data

    page.load_table_data()
    page.create(destination)


if __name__ == "__main__":
    subdir = "webpage"

    for year in range(2018, 2021+1):
        # Set the minimum date, to keep the related charts aligned.
        min_date = datetime.date(year, 1, 1)
        create_webpage(F"{subdir}/fire_{year}.html", year, min_date)
