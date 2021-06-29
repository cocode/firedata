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

