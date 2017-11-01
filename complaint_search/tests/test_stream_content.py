from django.test import TestCase
from complaint_search.stream_content import (
    StreamCSVContent,
    StreamJSONContent,
)

class StreamContentTests(TestCase):

    def setUp(self):
        pass

    def test_iter(self):
        sc = StreamCSVContent(None, iter([1,2,3]))
        self.assertTrue(isinstance(iter(sc), StreamCSVContent))

    def test_next_no_header(self):
        sc = StreamCSVContent(None, iter([1,2,3]))
        content = [ item for item in sc ]
        self.assertListEqual([1,2,3], content)


    def test_next_header(self):
        sc = StreamCSVContent("header", iter([1,2,3]))
        content = [ item for item in sc ]
        self.assertListEqual(["header",1,2,3], content)
