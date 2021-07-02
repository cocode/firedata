import os
import tempfile
from unittest import TestCase

from data_store import DataStore
from webpage import create_webpage_multi


class TestWebPage(TestCase):
    # Caution! Has to be run from 'firedata' directory, not 'firedata/webpage'.
    # pytest does this, but PyCharm doesn't by default
    def test_create(self):
        with tempfile.NamedTemporaryFile() as f:
            destination = f.name
            # Just test that it creates the file
            create_webpage_multi.create_webpage(destination, 2019, "CA")
            self.assertTrue(os.path.exists(destination))

    # Caution! Has to be run from 'firedata' directory, not 'firedata/webpage'.
    # pytest does this, but PyCharm doesn't by default
    def test_run(self):
        with tempfile.TemporaryDirectory() as dest_dir:
            # NY doesn't have its own template, so hits that path.
            create_webpage_multi.run(dest_dir, ["program_name", "AZ,CA,NY", "2021"])
            # Just test that it creates the file with the correct names.
            self.assertTrue(os.path.exists(os.path.join(dest_dir, "fire_az_2021.html")))
            self.assertTrue(os.path.exists(os.path.join(dest_dir, "fire_ca_2021.html")))
            self.assertTrue(os.path.exists(os.path.join(dest_dir, "fire_ny_2021.html")))
            # Check that we validate the state.
            with self.assertRaises(ValueError):
                create_webpage_multi.run(dest_dir, ["program_name", "ZZ", "2021"])


#     def test_load_historical_data(self):
#         self.fail()
#
#     def test_load_calfire_year_data(self):
#         self.fail()
#
#     def test_load_us_helper(self):
#         self.fail()
#
#     def test_load_us_data(self):
#         self.fail()
#
#     def test_load_chart_data(self):
#         self.fail()
#
#     def test_get_us_data(self):
#         self.fail()
#
#     def test_write_chart_begin(self):
#         self.fail()
#
#     def test_write_chart_options(self):
#         self.fail()
#
#     def test_write_chart_data(self):
#         self.fail()
#
#     def test_write_chart_end(self):
#         self.fail()
#
#     def test_write_chart(self):
#         self.fail()
#
#     def test_write_onload_begin(self):
#         self.fail()
#
#     def test_write_onload_end(self):
#         self.fail()
#
#     def test_write_onload_script(self):
#         self.fail()
#
#     def test_write_head(self):
#         self.fail()
#
#     def test_write_body_charts(self):
#         self.fail()
#
#     def test_write_summary(self):
#         self.fail()
#
#     def test_write_footer(self):
#         self.fail()
#
#     def test_write_body(self):
#         self.fail()
#
#     def test_write_document(self):
#         self.fail()
#
