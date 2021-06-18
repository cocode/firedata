# FireData Project
[![Fetch and Build](https://github.com/cocode/firedata/actions/workflows/fetch.yml/badge.svg)](https://github.com/cocode/firedata/actions/workflows/fetch.yml)

Project Status: Under development

This project displays data about the California fire season. It collects data from 
Cal Fire, and other sources, and create charts. The chart can be viewed here: 
https://cocode.github.io/firedata/

## Data 
This project scrapes data from [Cal Fire](https://www.fire.ca.gov/incidents), and other sites. 

### Data Collection
A github action is run every night (CA time) to fetch data.

### About Cal Fire Data:
Cal Fire data is just for fires handled by the organization "Cal Fire". Lots of fires are not handled by Cal Fire. 
I believe fires in national parks are not in Cal Fire data, nor are locally handled fires.

Cal Fire data gives you a snapshot of the days activity, and a list of fires for the year. 
To graph fires over time FireData collects a snapshot once a day.

*Note* that fire data can vary unexpectedly. Last year (2020) to total
acres burned reported in the json data dropped 1 m acres on 9/21.
I do not currently know why. And last year's Cal Fire json data shows "AllAcres" as 1,280,426 acres at the end of the
year but the Cal Fire summary says 4.1m acres in total.

Prior to 2021-06-16 I was collecting the data manually, so there are gaps
in the data.

#### Cal Fire JSON Format
The json has three main subsections (Incidents, ListIncidents, and AllYearIncidents). So far, it looks
like Incidents and ListIncidents are the same: currently burning fires. AllYearIncidents is what 
the name says.

Total acres burned for the year, as of the time the data was collected, is a top level field "AllAcres"

### Non Cal Fire Data
Non-Cal Fire data is not completely implemented yet. Fetchers 
for Washington state data, and Federal data exist, but were
broken in the move to github actions. They should be repaired shortly.

## Running FireData
You shouldn't need to run it yourself, this is a hosted solution. 

Take a look at fetch.sh in this directory, it's the code used
in the github action to fetch the data, and build the webpage.


# Similar Sites
https://calfireslo.org/current-slu-vegetation-fire-statistics/

# Resources
* https://www.fire.ca.gov/stats-events/
* https://www.fire.ca.gov/media/11397/fires-acres-all-agencies-thru-2018.pdf
  * All fires, 1987-2018, all agencies.
  * resulting data extracted to data/data_cal_annual
* https://www.fire.ca.gov/media/iy1gpp2s/2019_redbook_final.pdf
* https://osfm.fire.ca.gov/divisions/wildfire-planning-engineering/california-incident-data-and-statistics-program/
* https://www.sdge.com/sites/default/files/regulatory/CalFire%20Incident%20Information.pdf
* https://emlab.msi.ucsb.edu/sites/emlab.msi.ucsb.edu/files/wildfire-brief.pdf
* https://osfm.fire.ca.gov/divisions/wildfire-planning-engineering/california-incident-data-and-statistics-program/archived-statistic-reports/
* https://www.fire.ca.gov/programs/fire-protection/reports/

