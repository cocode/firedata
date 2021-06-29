from unittest import TestCase

from statistics import Statistics


class TestStatistics(TestCase):
    def test_verify_ids_unique(self):
        s = Statistics()
        data = [
            {
                "a":1,
                "id":12
            },
            {
                "b":1,
                "id":12
            }
        ]
        get_unique_id = lambda x: x["id"]
        with self.assertRaises(Exception):
            s.verify_ids_unique(data, get_unique_id)
        data[0]['id'] = 99
        # Should not raise now.
        s.verify_ids_unique(data, get_unique_id)

    def test_get_annual_acres(self):
        data = [
            { # Day 1
                "data":[
                    {"name": "unchanged", "id": 1, "acres": 100},
                    {"name": "increasing", "id": 2, "acres": 100},
                    {"name": "decreasing", "id": 3, "acres": 100},
                    {"name": "vanished", "id": 4, "acres": 100},

                ],
                "_year": 2021,
                "_month": 6,
                "_day": 28
            },
            {  # Day 2
                "data": [
                   {"name": "unchanged", "id": 1, "acres": 100},
                    {"name": "increasing", "id": 2, "acres": 101},
                    {"name": "decreasing", "id": 3, "acres": 98},

                    {"name": "new", "id": 5, "acres": 3}, # +2 total
                ],
                "_year": 2021,
                "_month": 6,
                "_day": 29
            },
            {  # Day 3
                "data": [
                    {"name": "unchanged", "id": 1, "acres": 100},
                    {"name": "increasing", "id": 2, "acres": 102},
                    {"name": "decreasing", "id": 3, "acres": 96},
                    {"name": "new", "id": 5, "acres": 6}, # +2 since day 1
                ],
                "_year": 2021,
                "_month": 6,
                "_day": 30
            }
        ]

        s = Statistics()
        daily, overall_total_acres_burned = s.get_annual_acres_helper(data, 2021, None, lambda x:x['id'], lambda x:x['acres'])
        self.assertEqual((2021, 6, 28, 400), daily[0])
        self.assertEqual((2021, 6, 29, 2), daily[1])
        self.assertEqual((2021, 6, 30, 2), daily[2])
        self.assertEqual(overall_total_acres_burned, 404)


    def test_get_annual_acres2(self):
        data = [
            { # Day 1
                "data":[
                    {"name": "unchanged", "id": 1, "acres": 100},
                ],
                "_year": 2021,
                "_month": 6,
                "_day": 28
            },
            {  # Day 2
                "data": [
                   {"name": "unchanged", "id": 1, "acres": 100},
                ],
                "_year": 2021,
                "_month": 6,
                "_day": 29
            },
            {  # Day 3
                "data": [
                    {"name": "unchanged", "id": 1, "acres": 100},
                    {"name": "new", "id": 2, "acres": 107},
                ],
                "_year": 2021,
                "_month": 6,
                "_day": 30
            }
        ]

        s = Statistics()
        daily, count = s.get_annual_acres_helper(data, 2021, None, lambda x:x['id'], lambda x:x['acres'])
        self.assertEqual(count, 3)
        self.assertEqual((2021, 6, 28, 100), daily[0])
        self.assertEqual((2021, 6, 29, 0), daily[1])
        self.assertEqual((2021, 6, 30, 107), daily[2])