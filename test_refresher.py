import json
import tempfile
from datetime import date, datetime
from unittest import TestCase
from unittest.mock import MagicMock, patch
import unittest.mock as mock
import refresher
from data_store import DataStore
import requests


class MyResponse:
    pass


class TestRefresh(TestCase):
    def test_refresh_with_mock(self):
        url = "https://example.com"
        mock_get = MagicMock()
        retval = MyResponse()
        retval.status_code = 200
        expected_data = {"AcresBurned":101}
        retval.content = bytes(json.dumps(expected_data, indent = 4), 'utf-8')  # Return dict as byte string

        mock_get.return_value = retval
        requests.get = mock_get
        with tempfile.TemporaryDirectory() as data_store_dir:
            def parse(x):
                return json.loads(x)
            ds = DataStore(data_store_dir)
            r = refresher.Refresh(url, ds, parse)
            today = date.today()
            r.refresh()
            mock_get.assert_called_once_with(url)
            data = ds.load_data_day(today)
            self.assertTrue(expected_data, data)
            all_data = ds.load_all_data()
            self.assertEqual(1, len(all_data))
            self.assertEqual(expected_data, all_data[0]['data'])


