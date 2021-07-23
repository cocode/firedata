# Fetch fire info for Arizona
from datetime import date

from refresher import Refresh
from data_store import DataStore
import bs4 as bs  # type: ignore
import re



DATA_STORE_PATH="data/data_az"


def get_data_store():
    data_store = DataStore(DATA_STORE_PATH)
    return data_store

# def summarize():
#     print()
#     print(F"Number of incidents.: {len(incidents):20,}")
#     print(F"New or growing fires: {growing_fires:20,}")
#     print(F"Total acres burned..: {acres_burned:>20,}")
#     print(F"New acres burned....: {acres_added:>20,}")


def parse(content):
    """
    Parse the page downloaded from the URL
    :param content: The text of the page.
    :return: List of dicts with incident data
    """
    soup = bs.BeautifulSoup(content)
    s = soup.prettify()
    t = re.sub("<.*?>", "", s)
    u = re.split("\\s+", t)
    u = u[1:]
    u = [x.replace(",","") for x in u]
    assert u[3]=="AZ"
    assert u[9]=="NM"
    today = date.today()
    return {
        "acres_burned": int(u[5]),
        "number_of_fires": int(u[4]),
        "date_saved":  today.strftime("%Y_%m_%d"),
        "_year": today.year,
        "_month": today.month
    }


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


def patch_test(a):
    def parse(a):
        return a
    refresher = Refresh("a", DataStore("/tmp"), parse)
    return refresher.pt(a)


def fetch():
    fire_url = 'https://gacc.nifc.gov/swcc/predictive/intelligence/intelligence.htm'
    # Subpage fetched from above page.
    fire_url = 'https://gacc.nifc.gov/swcc/predictive/intelligence/daily/UPLOAD_Files_toSWCC/YTD_10_INFORM_Protection_5_Website_Intell.csv'
    data_store = get_data_store()
    refresher = Refresh(fire_url, data_store, parse)
    refresher.refresh()   # Gets the data, only if we don't already have it.
    return data_store


def run(data_dir):
    fetch()


if __name__ == "__main__":
    run("data/data_az")           # pragma: no cover
    print("Done.")  # pragma: no cover