import os
from datetime import date
import json


class DataStore:
    """
    represents a set of snapshots of the data scraped from Cal Fire (and other fire info providers,
    but cal fire is the most complete).
    Since it is a snapshot, the data we pull doesn't have the date it was pulled, so we add this
    to the downloaded data, as _year, _month and _day.
    """
    def __init__(self, data_dir:str):
        self.data_dir = data_dir

    def get_data_dir(self):
        return self.data_dir

    def get_source_dir(self):
        """
        The directory where we store the source of the data we parse.
        We did not originally save this, so the will may not be present for all data.
        We did save it when back filling from the internet archive, so old source files to exist.
        :return:
        """
        return os.path.join(self.data_dir, "source")

    def get_filename(self, day: date):
        dstring = day.strftime("%Y_%m_%d")
        filename = F"{self.get_data_dir()}/firedata_{dstring}.json"
        return filename

    def get_source_filename(self, day: date, extension=".html"):
        """
        Get the filename to store the source data that we parse to get the actual data.
        :param day:
        :param extension: The file extension.
        :return:
        """
        dstring = day.strftime("%Y_%m_%d")
        filename = F"{self.get_source_dir()}/firedata_{dstring}.{extension}"
        return filename

    def save_source_data(self, data: str, day: date, force=False, extension=".html"):
        """
        Store the source data for the page we parse to get fire data.
        :param data:
        :param day:
        :param force:
        :param extension:
        :return: None
        """
        if not os.path.exists(self.get_source_dir()):
            os.mkdir(self.get_source_dir())
        filename = self.get_source_filename(day, extension=extension)
        if os.path.exists(filename) and not force:
            return
        with open(filename, "w") as f:
            f.write(data)
        return

    def get_source_data(self, day: date, extension=".html"):
        """
        Get the source data for the page we parse to get fire data.
        :param day:
        :param extension:
        :return: The data
        """
        if not os.path.exists(self.get_source_dir()):
            os.mkdir(self.get_source_dir())
        filename = self.get_source_filename(day, extension=extension)
        if not os.path.exists(filename):
            return

        with open(filename, "r") as f:
            data = f.read()
        return data

    def does_data_exist(self, day: date):
        filename = self.get_filename(day)
        return os.path.exists(filename)

    def save_date_data(self, date_of_data: date, fire_data):
        filename = self.get_filename(date_of_data)
        self.save_data(filename, fire_data)

    def save_todays_data(self, jdata):
        """
        Saves the data to a file, timestamped with today's date.
        :param jdata: Json data to save
        :return:
        """
        today = date.today()
        self.save_date_data(today, jdata)

    @staticmethod
    def save_data(filename: str, jdata):
        formatted = json.dumps(jdata, indent=4)
        a = os.path.abspath(filename)
        with open(filename, "w") as f:
            f.write(formatted)

    def load_all_data(self, filter_to_year=None, include=None):
        """
        Loads all the data in the data store, and wraps it in a dict, with
        metadata
        :param: filter_to_year - Only include data in the given year
        :param: include If not None, include(item)
        :return: A list of dicts, which contain metadata and the data
        """
        all_data = []
        if filter_to_year and type(filter_to_year) == int:
            filter_to_year = str(filter_to_year)
        # Maybe we should generate filenames by date, and look back?
        # This gives us two ways to create filenames.
        files = os.listdir(self.get_data_dir())
        files = sorted(files)
        for f in files:
            if not f.endswith(".json"):
                continue
            if not f.startswith("firedata_"):
                continue
            ff = f.split('_')
            year = ff[1]
            if filter_to_year is not None and filter_to_year != year:
                continue;
            month = ff[2]
            day = ff[3].split(".")[0]
            assert 2018 <= int(year) <= 2099
            assert 1 <= int(month) <= 12
            assert 1 <= int(day) <= 31
            filename = F"{self.get_data_dir()}/{f}"
            #print("FILENAME", filename)
            one_days_data = self.load_data_file(filename)
            if include is not None:
                # This may need more work to genearalize it. Working on it for US data source.
                one_days_data = [item for item in one_days_data if include(item)]
            # Wrap the returned data in a dict, with some metadata
            returned_data = {'data': one_days_data}
            returned_data["_filename"] = filename
            returned_data["_year"] = int(year)
            returned_data["_month"] = int(month)
            returned_data["_day"] = int(day)
            all_data.append(returned_data)
        return all_data

    def load_data_day(self, day:date):
        '''
        Loads that data from a particular day
        :param day:
        :return:
        '''
        filename = self.get_filename(day)
        return self.load_data_file(filename)

    @staticmethod
    def load_data_file(filename:str):
        #print(f"{filename}")
        with open(filename, "r") as f:
            string_data = f.read()
        j = json.loads(string_data)
        return j
