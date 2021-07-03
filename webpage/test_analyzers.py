import tempfile
from unittest import TestCase
from webpage import analyzers


class TestAnalyzers(TestCase):
    # Tests have to run from firedata dir, not firedata/webpage
    def test_get_data(self):
        a = analyzers.Analyzer({})
        self.assertEqual([], a.get_data(None))  # Mostly for the code coverage

    def test_analyzer_az(self):
        a = analyzers.AnalyzerAZ({})
        data = a.get_data(2021)
        self.assertTrue(len(data) > 0)

    def test_analyzer_wa(self):
        a = analyzers.AnalyzerWA({})
        data = a.get_data(2021)
        self.assertTrue(len(data) > 0)

    def test_analyzer_ca(self):
        a = analyzers.AnalyzerCalFire({})
        data = a.get_data(2021)
        self.assertTrue(len(data) > 0)
