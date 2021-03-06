"""
Compute daily statistics from fire data.
"""


class Statistics:
    def __init__(self):
        pass

    def verify_ids_unique(self, incidents, get_unique_id):
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

    def get_annual_acres_helper(self, all_data, year, previous_data=None, get_unique_id=None, get_size=None,cumulative=False):
        """
        Gets the number of acres burned, for each day of the current (or specified) year.
        Used to generate data for website graphs.

        This implementation is for sources that provide a daily value for each fire, and we have to
        look at the previous day's fires to compute the growth.

        I also have to look back to the last day before the year starts. Otherwise, on January 1,
        all fires seem to be new, so the number of acres burned all piles up on that one day.
        # TODO We should calculate the total acres when we save the data, and add it.

        :param all_data: All data for the specified year
        :param previous_data: All data for the year before that. We only need the last day of this.
        :param year: The year being summarized.
        :return: tuple of
            list of tuples of (year, month, day, acres_burned)
            int total acres burned
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
            # This is now filtered in the data store. Let's just assert it here, rather than filtering again.
            assert year is None or days_year == year
            days_total = 0

            # Make sure fire ids are unique.
            self.verify_ids_unique(day_data, get_unique_id)

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
            #acres_burned.append((days_year, meta_data["_month"], meta_data["_day"], days_total))
            overall_total_acres_burned += days_total
            if cumulative:
                acres_burned.append((days_year, meta_data["_month"], meta_data["_day"], overall_total_acres_burned))
            else:
                acres_burned.append((days_year, meta_data["_month"], meta_data["_day"], days_total))

        return acres_burned, overall_total_acres_burned
