import unittest

from complaint_search.defaults import MAX_PAGINATION_DEPTH, PAGINATION_BATCH
from complaint_search.es_interface import get_pagination_query_size


class TestPaginationSize(unittest.TestCase):
    def setUp(self):
        self.user_sizes = [10, 25, 50, 100]

    def test_get_pagination_query_size_page_1(self):
        page = 1
        for user_size in self.user_sizes[:3]:
            self.assertEqual(
                get_pagination_query_size(page, user_size),
                PAGINATION_BATCH * 2,
            )
        self.assertEqual(get_pagination_query_size(page, 400), 600)

    def test_get_pagination_query_size_page_2(self):
        page = 2
        self.assertEqual(
            get_pagination_query_size(page, 25), PAGINATION_BATCH * 2
        )
        self.assertEqual(
            get_pagination_query_size(page, 100), PAGINATION_BATCH * 4
        )

    def test_get_pagination_query_size_with_remainder(self):
        page = 6
        self.assertEqual(
            get_pagination_query_size(page, 25), PAGINATION_BATCH * 4
        )

    def test_get_pagination_query_size_equals_max(self):
        page = 100
        self.assertEqual(
            get_pagination_query_size(page, 100), MAX_PAGINATION_DEPTH
        )

    def test_get_pagination_query_size_exceeds_max(self):
        page = 101
        self.assertEqual(
            get_pagination_query_size(page, 100), MAX_PAGINATION_DEPTH
        )
