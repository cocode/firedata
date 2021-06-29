import tempfile
from unittest import TestCase
from analyzers import Analyzer


class TestAnalyzers(TestCase):
    def test_get_data(self):
        a = Analyzer({})
        self.assertEqual([], a.get_data(None))  # Mostly for the code coverage