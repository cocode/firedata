# Fetch fire info from cal fire.

# source

# TODO Should frst fetch and cache raw page. Then parse from there. That way I don't have to
# refetch when debugging parser.
# also would make changing the data I pull better. I was discarding other states during parsing
# of us data, so now I don't have historical data for the other states

from refresher import Refresh
from data_store import DataStore
import bs4 as bs  # type: ignore


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

    incidents = jdata_today['data']
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
            yesterday_data = yesterday['data']
            yes = [item for item in yesterday_data if get_id(item) == id]
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


def get_annual_acres(ds:DataStore, year:int):
    """
    Gets the number of acres burned, for each day of the current (or specified) year.
    Used to generate data for website graphs.

    :param ds:
    :param year:
    :return: list of tuples (year, month, day, acres burned that day).
    """
    all_data = ds.load_all_data(year)
    acres_burned = []
    for meta_data in all_data:
        day_data = meta_data['data']
        days_year = meta_data["_year"]
        if days_year != year:
            continue
        ab = day_data['acres_burned']
        ab = int(ab)
        acres_burned.append((days_year, meta_data["_month"], meta_data["_day"], ab))
    return acres_burned, len(all_data)


def get_unique_id(incident):
    """
    Gets a unique id for this incident.
    Originally, we just used href as a unique, but sometimes fires don't get their own URL, and
    get the default "/incident//", or even None.
    :param incident:
    :return:
    """
    has_num = 'Incident Number' in incident
    has_name = 'Incident Name' in incident
    if has_num:
        return incident['Incident Number']

    if has_name:
        name = incident['Incident Name']

    raise Exception(F"No unique id for incident {incident}")


def verify_ids_unique(incidents):
    """
    Make sure fire ids are unique. Don't trust your data sources!
    Raises an Exception on duplicate
    :param incidents:
    :return: None
    """
    check_unique = set()
    for incident in incidents:
        unique_fire_id = get_unique_id(incident)
        if unique_fire_id in check_unique:
            raise Exception(F"Fire ID not unique: {unique_fire_id}")
        check_unique.add(unique_fire_id)


def get_annual_acres_helper(all_data, year, previous_data=None):
    """
    TODO Merge this with the version in get_us_fire_data. Maybe common parent class?
    Gets the number of acres burned, for each day of the current (or specified) year.
    Used to generate data for website graphs.

    Unlike cal fire data, where I can just look like a top-level field, I think
    for US I must sum all incidents on each day, then subtract the previous day's
    value, on  a per fire basis.

    I also have to look back to the last day before the year starts. Otherwise, on January 1,
    all fires seem to be new, so the number of acres burned all piles up on that one day.

    # TODO Find a better data source.
    # TODO We should calculate the total acres when we save the data, and add it.

    :param all_data: All data for the specified year
    :param previous_data: All data for the year before that. We only need the last day of this.
    :param year: The year being summarized.
    :return: list of tuples of (year, month, day, acres_burned)
    """
    acres_burned = []
    last_burned = {}
    # Get a starting point for how much has burned, so we don't put is all on January 1st this year.
    # These are all the fires that were burning at the end of the previous year.
    if year is not None and previous_data:
        meta_data = previous_data[-1]
        day_data = meta_data['data']
        for incident in day_data:
            unique_fire_id = get_unique_id(incident)
            burned_as_of_today = get_size(incident)
            last_burned[unique_fire_id] = burned_as_of_today

    overall_total_acres_burned = 0
    for meta_data in all_data:
        day_data = meta_data['data']
        days_year = meta_data["_year"]
        if year is not None and days_year != year:
            continue
        days_total = 0

        # Make sure fire ids are unique.
        verify_ids_unique(day_data)

        for incident in day_data:
            unique_fire_id = get_unique_id(incident)
            ab = get_size(incident)
            if ab:
                burned_as_of_today = int(ab)  # What is this fire's total burned acres, as of today.
                # Compute delta between current total for this fire, and yesterdays, so we get
                # acres burned today.
                if unique_fire_id in last_burned:
                    previous_total = last_burned[unique_fire_id]
                    last_burned[unique_fire_id] = burned_as_of_today
                    change_in_acres_burned = burned_as_of_today - previous_total  # Get change since last data point.
                else:
                    # New fire. Change is total acres burned today.
                    change_in_acres_burned = burned_as_of_today
                    last_burned[unique_fire_id] = burned_as_of_today

                days_total += change_in_acres_burned
        acres_burned.append((days_year, meta_data["_month"], meta_data["_day"], days_total))
        overall_total_acres_burned += days_total
    return acres_burned, overall_total_acres_burned


def get_annual_acres(ds:DataStore, year, state=None):
    all_data = ds.load_all_data(year)
    if year is None:
        previous_data = None
    else:
        # TODO This doesn't work, if we use the create_webpage option to start the graph at other than the first day.
        previous_data = ds.load_all_data(year - 1)
    return get_annual_acres_helper(all_data, year=year, previous_data=previous_data)


def parse(content):
    """
    Parse the page downloaded from the URL
    :param content: The text of the page.
    :return: List of dicts with incident data
    """
    soup = bs.BeautifulSoup(content)
    fieldsets = soup.find_all("fieldset")
    print(F"Found {len(fieldsets)} fields.")
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
    print(F"JSON data parsing. Found = {len(all_fires)} fires.")
    return all_fires

def get_data_store():
    data_store = DataStore("data/data_wa")
    return data_store

def run():
    fire_url = 'https://gacc.nifc.gov/nwcc/information/fire_info.aspx'
#    fire_url = 'file:///Users/tom/PycharmProjects/Pandas/fire/data_wa/sample.html'
    data_store = get_data_store()
    refresher = Refresh(fire_url, data_store, parse)
    refresher.refresh()   # Gets the data, only if we don't already have it.
    summarize(data_store)
    all_fires, days = get_annual_acres(data_store, 2021)
    print(all_fires)


if __name__ == "__main__":
    run()
    print("Done.")