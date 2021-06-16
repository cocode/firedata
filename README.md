# FireData
Project Status: Under development

This project displays data about the California fire season.

The data can be viewed here: https://cocode.github.io/firedata/

This project scrapes data from cal fire, and other sites. CalFire's
incident site doesn't directly provide the information I wanted,
nor visualizations:
* Is the number of acres burning going up or down?
* Graphs

# Running FireData
Take a look at fetch.sh in this directory, it's the code used
in the github action to fetch the data, and build the webpage.


Currently, this is run manually every day, and prints the number of acres burned since yesterday. 
The goal is to automate this, and make it public. 
Something like this: https://calfireslo.org/current-slu-vegetation-fire-statistics/

### Cal Fire Data:
Note that cal fire data is just for the organization "cal fire". Lots of fires are not cal fire. For example,
fires in national parks are not in this data, I believe. That may be in the US data,
which is not in the graph yet. Other local fires may not be reported by Cal Fire.

Last year's Cal Fire data shows "AllAcres" as 1280426, but news reports say 4.7m in total. 


#### Cal Fire JSON Format
The json has three main subsections (Incidents, ListIncidents, and AllYearIncidents). So far, it looks
like Incidents and ListIncidents are the same: Currently burning fires. AllYearIncidents is what is
says.

Total acres burned for the year is a top level field "AllAcres"

# Non Cal Fire Data
Non-Cal Fire data is not completely implemented yet.

