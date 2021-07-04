import os
from unittest import TestCase
from unittest.mock import patch, mock_open

import make_badge
import tempfile

class Test(TestCase):
    def test_run(self):
        with tempfile.TemporaryDirectory() as d:
            # Does the CWD get reset after this test?
            os.chdir(d)
            print("a")
            with open("coverage.txt", "w") as f:
                f.write("15%")
            print("b")
            make_badge.run()
            with open("code-coverage.txt") as f:
                blob = f.read()
        expected ="""{
    "schemaVersion": 1,
    "label": "coverage",
    "message": "15%",
    "color": "orange"
}"""
        self.assertEqual(expected,  blob)
