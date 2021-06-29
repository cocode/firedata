import tempfile
from unittest import TestCase
from webpage import analyzers


class TestAnalyzers(TestCase):
    def test_get_data(self):
        a = analyzers.Analyzer({})
        self.assertEqual([], a.get_data(None))  # Mostly for the code coverage