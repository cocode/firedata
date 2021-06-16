# Fetch fire info from cal fire.

# source

# TODO Should frst fetch and cache raw page. Then parse from there. That way I don't have to
# refetch when debugging parser.
# also would make changing the data I pull better. I was discarding other states during parsing
# of us data, so now I don't have historical data for the other states

import requests
import sys
import json
from datetime import date
import os


# Keys in the json blob returned from cal fire. I only care about "Incidents"
# Incidents
# MatchedIncidentCount
# AllAcres
# AllIncidentCount
# AllFatalities
# AllStructures
# ListIncidents
# AllYearIncidents
from requests import HTTPError
from refresher import Refresh
from data_store import DataStore
import bs4 as bs


def get_size(x):
    if x is None:
        return 0
    s = None
    if 'Acres' in x:
        s = x['Acres']
    if not s:
        return 0
    y = s.split()
    z = y[0]
    zz = z.replace(",","")
    q = int(zz)
    return q


def get_containment(x):
    if x is None:
        return 0
    s = None
    if "Percent Contained" in x:
        s = x["Percent Contained"]
    if not s:
        return 0
    zz = s.replace("%","")
    q = int(zz)
    return q


# f-strings in python suck at handling None, so this class helps
def sub(fire, key, width, f=None):
    ty = type(fire[key])
    if ty == str:
        v = int(fire[key].replace("%", ""))
    else:
        v = fire[key]
    if key in fire and fire[key] is not None:
        value = F"{v:{width},}"
    else:
        value = F"{'~':>{width}}"
    return value


def get_id(fire):
    return fire["Incident Number"]


# Could also use from operator import itemgetter, attrgetter
def summarize(ds):
    dwidth = 10
    awidth = 14
    pwidth = 5 # percentage field width (for containment)

    jdata = ds.load_all_data()
    jdata_today = jdata[-1]
    if len(jdata) > 1:
        yesterday = jdata[-2]
    else:
        yesterday = None

    print(F"{'Acres Burned':>{awidth}} {'Change':>{dwidth}} {'%Cont':>{pwidth}} {'Change':>{dwidth}}  {'Incident Name'}")

    incidents = jdata_today
    # already sorted for us by loader
    acres_burned = 0
    acres_added = 0 # Number of new acres burned.
    growing_fires = 0
    for fire in incidents:
        ab = get_size(fire) # TODO changed from cal_file
        if ab is not None:
            acres_burned += ab # changed
        contained = get_containment(fire) # TODO changed from cal_file
        if yesterday:
            id = get_id(fire)
            yes = [item for item in yesterday if get_id(item) == id]
            assert len(yes) < 2
            f2 = yes[0] if len(yes) else None
            old_size = get_size(f2)
            if ab and f2 and old_size and (old_size != ab):
                delta_a = ab - get_size(f2)
                acres_added += delta_a
                if delta_a:
                    growing_fires += 1
                delta_a = F"{delta_a:>+{dwidth}}"
            else:
                delta_a = F"{' ':{dwidth}}"
            old_contained = get_containment(f2)
            if contained and f2 and old_contained and (old_contained != contained):
                delta_c = contained - old_contained
                delta_c = F"{delta_c:>+{dwidth}}"
            else:
                delta_c = F"{' ':{dwidth}}"

            print(F"{get_size(fire):{awidth},} {delta_a} {sub(fire,'Percent Contained',pwidth)} {delta_c} {fire['Incident Name']}")
        else:
            print(F"{get_size(fire):{awidth},}   {fire['Incident Name']}")

    print()
    print(F"Number of incidents.: {len(incidents):20,}")
    print(F"New or growing fires: {growing_fires:20,}")
    print(F"Total acres burned..: {acres_burned:>20,}")
    print(F"New acres burned....: {acres_added:>20,}")


def parse(content):
    """
    Parse the page downloaded from the URL
    :param content: The text of the page.
    :return: List of dicts with incident data
    """
    soup = bs.BeautifulSoup(content, "html5lib")
    fieldsets = soup.find_all("fieldset")
    #    fieldsets = soup.find_all("fieldset", {"summary":"This table displays all active incidents."})
    #print(fieldsets)
    all_fires = []
    for inum, fieldset in enumerate(fieldsets):
        legend = fieldset.find("legend")
        if legend.text != "General Info":
            continue
        # One fire
        fire = {}
        table = fieldset.find("table")
        if table is None:
            print(f"None table {fieldset}")
            continue
        fields = table.find_all("td")
        for field in fields:
            label = field.find("label")
            text = field.text
            label_text = label.text
            if len(text) > len(label_text):
                text = text[len(label_text):].strip()
            if label and text is not None:
                label_text = label.text
                #print(F"inum {inum} Label {label_text}, text {text}")
                fire[label_text] = text
            else:
                raise Exception(F"Bad field {field} {label} {text}")

        #print(json.dumps(fire, indent=4))
        all_fires.append(fire)
    all_fires = sorted(all_fires, key=get_size, reverse=True)
    return all_fires


def run():
    fire_url = 'https://gacc.nifc.gov/nwcc/information/fire_info.aspx'
#    fire_url = 'file:///Users/tom/PycharmProjects/Pandas/fire/data_wa/sample.html'
    data_store = DataStore("data/data_wa")
    refresher = Refresh(fire_url, data_store, parse)
    refresher.refresh()   # Gets the data, only if we don't already have it.
    summarize(data_store)


if __name__ == "__main__":
    run()
    print("Done.")