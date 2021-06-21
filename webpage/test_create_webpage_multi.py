from unittest import TestCase
from webpage import create_webpage_multi


class TestWebPage(TestCase):
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
        def test_create(self):
            create_webpage_multi.create_webpage(2021)
