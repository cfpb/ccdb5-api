import unittest

from complaint_search.es_interface import get_break_points
from complaint_search.tests.es_interface_test_helpers import load


class TestBreakPoints(unittest.TestCase):

    def setUp(self):
        self.test_data = load("break_point_data")

    def test_get_break_points_none(self):
        break_points = get_break_points(
            self.test_data.get("hits"), size=25)
        self.assertEqual(break_points, {})

    def test_get_break_points_single(self):
        target_break_point = self.test_data["hits"][9].get("sort")
        break_points = get_break_points(
            self.test_data.get("hits"), size=10)
        self.assertEqual(len(break_points), 1)
        self.assertEqual(break_points[2], target_break_point)

    def test_get_break_points_multiple(self):
        target_break_point = self.test_data["hits"][3].get("sort")
        break_points = get_break_points(
            self.test_data.get("hits"), size=2)
        self.assertEqual(len(break_points), 5)
        self.assertEqual(break_points[3], target_break_point)
