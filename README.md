# FireData Project
[![Fetch and Build](https://github.com/cocode/firedata/actions/workflows/fetch.yml/badge.svg)](https://github.com/cocode/firedata/actions/workflows/fetch.yml)
[![Run Tests](https://github.com/cocode/firedata/actions/workflows/run_tests.yml/badge.svg)](https://github.com/cocode/firedata/actions/workflows/run_tests.yml)
![Code Coverage](https://img.shields.io/endpoint?style=flat&url=https%3A%2F%2Fraw.githubusercontent.com%2Fcocode%2Ffiredata%2Fmaster%2Fcode-coverage.txt)

Project Status: Under development

This project displays data about the fire season for the selected year.
It collects data from US Fire data, Cal Fire, and other sources, and creates charts.
The chart can be viewed here: https://cocode.github.io/firedata/


## Data 
This project scrapes data from [Cal Fire](https://www.fire.ca.gov/incidents), and other sites. 

There are a number of issues in the data. Different sites do not agree. Sometimes a site will not
agree with itself! CalFire incidents has one number on its home page, and you get another, smaller number if
you add up all the fires listed. And sometimes the fires listed will grow, but the main page number
doesn't change. From this, I suspect the main page may 1) be manually updated, and 2) The main number
may include other fires managed by other entities, like local fire departments.

Cal fire also has fires that "go away". Between July 7th and 8th, Cal Fire's ***cumulative*** total
went down. This is due to the "Lava Fire" have it's "AcresBurnedDisplay" field go from "25,001" to "" overnight.
I suspect this is due to the fire being handed off to another entity. The notation on the Lava fire says
"Not a CAL FIRE Incident as of 7/07/2021". 

Other possible sources of error:

* The data is frequently not documented, so I may be intepreting the data incorrectly. (See "Lava Fire" above)
* There may be bugs in my scraping code. 
* Original data may be an estimate, and this may be corrected over time
* Sources may not always update consistently. 

### Data Collection
A github action is run every night (CA time) to fetch data.
These sources do not provide historical data, so the data is fetched, and checked into github in the data directory.


### About Cal Fire Data:
Cal Fire data is just for fires handled by the organization "Cal Fire". Lots of fires are not handled by Cal Fire. 
I believe fires in national parks are not in Cal Fire data, nor are locally handled fires.

Cal Fire data gives you a snapshot of the days activity, and a list of fires for the year. 
To graph fires over time FireData collects a snapshot once a day.

*Note* that fire data can vary unexpectedly. Last year (2020) to total
acres burned reported in the json data dropped 1 m acres on 9/21.
I do not currently know why. And last year's Cal Fire json data shows "AllAcres" as 1,280,426 acres at the end of the
year but the Cal Fire summary says 4.1m acres in total. My guess is that 1.28M is what Cal Fire handled directly, 
with federal and local agencies handling the rest of the 4.1M.

Prior to 2021-06-16 I was collecting the data manually, so there are gaps
in the data. I did back-fill some from the internet archive. '

#### Cal Fire JSON Format
The json has three main subsections (Incidents, ListIncidents, and AllYearIncidents). So far, it looks
like Incidents and ListIncidents are the same: currently burning fires. AllYearIncidents appears to be what 
the name says.

Total acres burned for the year, as of the time the data was collected, is a top level field "AllAcres"

### Non Cal Fire Data
Non-Cal Fire data is not completely implemented yet. We have fetch code for a couple of states, for others
we just present federal data.

## Running FireData
You shouldn't need to run it yourself, this is a hosted solution. 

But if you still want to, take a look at fetch.sh in this directory, it's the code used
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
* US Fire Administration  
  * https://www.usfa.fema.gov/nfirs/
  * https://www.usfa.fema.gov/index.html
  * https://www.usfa.fema.gov/wui/data/nfirs-wildland-module.html - how do I get this data?
  * "historically, NFIRS data have not proved useful in understanding the nature and magnitude of the wildland fire problem. The optional Wildland Fire Module attempts to rectify this"
  * all the data, but free form: https://gacc.nifc.gov/swcc/predictive/intelligence/daily/SWCC_Morning_Situation_Report/SWCC_Morning_Situation_Report.htm
  * Good, by state: https://www.nifc.gov/fire-information/nfn
  
