import datetime

import get_az_fire_data
import get_ca_alt_fire_data
import get_us_fire_data
import get_ca_fire_data
import get_historical_data
import re, json
import io

import get_wa_fire_data


class Analyzer:
    def __init__(self, env):
        self.env = env

    def get_data(self, year, x_min_date=None):
        return []


class AnalyzerUs(Analyzer):
    """
    Analyzer that pulls one state's information from the federal data.
    Also base class for specific states.
    """

    def __init__(self, env):
        super(AnalyzerUs, self).__init__(env)
        self.state = None # All states

    def helper(self, year, state=None, x_min_date=None):
        if state == None:
            state = self.state
        data_source = get_us_fire_data.get_data_store()
        acres_burned, days_of_data_found = get_us_fire_data.get_annual_acres(data_source, year=year, state=state)
        # TODO Could make this a shared method, but would need to know number of columns to create.
        # If we want to start the chart at say, May 1st, we need to put in a dummy data point for the chart.
        data_as_string = ""
        if x_min_date and len(acres_burned) > 0:
            current_min = datetime.date(year, acres_burned[0][1], acres_burned[0][2])
            if current_min > x_min_date:
                # if acres_burned[0][1] != 1 or acres_burned[0][2] != 1:
                data_as_string += F"[new Date({year}, {x_min_date.month - 1}, {x_min_date.day}), {0}],\n"

        for i in acres_burned:
            ab = i[3]
            data_as_string += F"[new Date({i[0]}, {i[1] - 1}, {i[2]}), {ab}],\n"
        return data_as_string

    def get_data(self, year, x_min_date=None):
        return self.helper(year, x_min_date=x_min_date)


class AnalyzerUsCa(AnalyzerUs):
    def __init__(self, env):
        super(AnalyzerUsCa, self).__init__(env)

    def get_data(self, year, x_min_date=None):
        return self.helper(year, "California", x_min_date)


class AnalyzerUsXX(AnalyzerUs):
    """
    Analyzer that pulls one state's information from the federal data.
    """
    # TODO This can be merged with AnalyserUs
    def __init__(self, env):
        super(AnalyzerUsXX, self).__init__(env)
        self.state = env['state']

    def get_data(self, year, x_min_date=None):
        return self.helper(year, None, x_min_date)


class AnalyzerStateBase(Analyzer):
    def __init__(self, env):
        super(AnalyzerStateBase, self).__init__(env)
        self.module = None

    def get_data(self, year, x_min_date=None):
        """
        Loads the data from self.year. Also generates the summary info printed
        below the chart.
        :return:
        """
        data_source = self.module.get_data_store()
        acres_burned, days_of_data_found = self.module.get_annual_acres(data_source, year=year)

        data_as_string = ""
        if x_min_date and len(acres_burned) > 0:
            current_min = datetime.date(year, acres_burned[0][1], acres_burned[0][2])
            if current_min > x_min_date:
                # if acres_burned[0][1] != 1 or acres_burned[0][2] != 1:
                data_as_string += F"[new Date({year}, {x_min_date.month - 1}, {x_min_date.day}), {0}],\n"

        for i in acres_burned:
            data_as_string += F"[new Date({i[0]}, {i[1] - 1}, {i[2]}), {i[3]}],\n"
        return data_as_string


class AnalyzerCalFire(AnalyzerStateBase):
    def __init__(self, env):
        super(AnalyzerCalFire, self).__init__(env)
        self.module = get_ca_fire_data


class AnalyzerCalAltFire(AnalyzerStateBase):
    def __init__(self, env, get_ca__alt_fire_data=None):
        super(AnalyzerCalAltFire, self).__init__(env)
        self.module = get_ca_alt_fire_data


class AnalyzerCaHistorical(Analyzer):
    def __init__(self, env):
        super(AnalyzerCaHistorical, self).__init__(env)

    def get_data(self, year, x_min_date=None):
        historical = get_historical_data.get_stats()
        hist_string = ""
        for y in historical:
            acres = y[2]
            fed_acres = y[4]
            local_acres = y[6]
            acres = acres.replace(",", "")
            fed_acres = fed_acres.replace(",", "")
            local_acres = local_acres.replace(",", "")
            # Javascript counts months from 0-11, so december is 11
            hist_string += F'[new Date({y[0]}, 11, 31), {acres}, {fed_acres}, {local_acres}],\n'
        return hist_string


class AnalyzerAZ(AnalyzerStateBase):
    def __init__(self, env):
        super(AnalyzerAZ, self).__init__(env)
        self.module = get_az_fire_data


class AnalyzerWA(AnalyzerStateBase):
    def __init__(self, env):
        super(AnalyzerWA, self).__init__(env)
        self.module = get_wa_fire_data

