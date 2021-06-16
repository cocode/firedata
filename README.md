# FireData
Project Status: Under development

This project scrapes data from cal fire, and other sites. CalFire's
incident site doesn't directly provide the information I wanted,
nor visualizations:
* Is the number of acres burning going up or down?
* Graphs

# Running FireData
running (in the firedata directory)
    python get_cal_fire_data.py
y will start fetching the current day's
data, if it's not already in the repository.

running (in the firedata/webpage directory)
    python create_webpage.py
Will build "fire_graphs.html" in that directory, which uses
google charts to graph fire information.

Currently, this is run manually every day, and prints the number of acres burned since yesterday. 
The goal is to automate this, and make it public. 
Something like this: https://calfireslo.org/current-slu-vegetation-fire-statistics/

### Cal Fire Data:
Note that cal fire data is just for the organization "cal fire". Lots of things are not cal fire. Last
year's data shows "AllAcres" as 1280426, but news reports say 4.7 in total. There is US data as well, 
which is not in the graph yet. Other local fires may not be reported
in either calfire or US reports.

#### Cal Fire JSON Format
The json has three main subsections (Incidents, ListIncidents, and AllYearIncidents). So far, it looks
like Incidents and ListIncidents are the same: Currently burning fires. AllYearIncidents is what is
says.

Total acres burned for the year is a top level field "AllAcres"

# Non Cal Fire Data
Non-Cal Fire data is not completely implemented yet.

