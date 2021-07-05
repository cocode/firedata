import os
from unittest import TestCase

import make_badge
import tempfile


class Test(TestCase):
    def test_run(self):
        with tempfile.TemporaryDirectory() as d:
            # Does the CWD get reset after this test? NO!!
            # Changing the CWD causes later tests to fail with very non-obvious errors
            # from pytest.
            cwd = os.getcwd()
            try:
                os.chdir(d)
                print("a")
                with open("coverage.txt", "w") as f:
                    f.write("15%")
                print("b")
                make_badge.run()
                with open("code-coverage.txt") as f:
                    blob = f.read()
            finally:
                os.chdir(cwd)

        expected ="""{
    "schemaVersion": 1,
    "label": "coverage",
    "message": "15%",
    "color": "orange"
}"""
        self.assertEqual(expected,  blob)
