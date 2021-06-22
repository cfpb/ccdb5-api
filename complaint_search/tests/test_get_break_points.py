import json
import unittest
from os.path import dirname, realpath

from complaint_search.es_interface import get_break_points

search_dir = dirname(dirname(realpath(__file__)))


class TestBreakPoints(unittest.TestCase):

    def setUp(self):
        self.test_file = f"{search_dir}/fixtures/break_point_data.json"

    def test_get_break_points_none(self):
        with open(self.test_file, "r") as f:
            test_data = json.loads(f.read())
        break_points = get_break_points(
            test_data.get("hits"), size=25)
        self.assertEqual(break_points, {})

    def test_get_break_points_single(self):
        with open(self.test_file, "r") as f:
            test_data = json.loads(f.read())
        target_break_point = test_data["hits"][9].get("sort")
        break_points = get_break_points(
            test_data.get("hits"), size=10)
        # import pdb; pdb.set_trace()
        self.assertEqual(len(break_points), 1)
        self.assertEqual(break_points[2], target_break_point)

    def test_get_break_points_multiple(self):
        with open(self.test_file, "r") as f:
            test_data = json.loads(f.read())
        target_break_point = test_data["hits"][3].get("sort")
        break_points = get_break_points(
            test_data.get("hits"), size=2)
        self.assertEqual(len(break_points), 5)
        self.assertEqual(break_points[3], target_break_point)
