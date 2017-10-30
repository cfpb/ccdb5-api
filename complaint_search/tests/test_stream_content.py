from django.test import TestCase
from complaint_search.stream_content import StreamContent

class StreamContentTests(TestCase):

    def setUp(self):
        pass

    def test_iter(self):
        sc = StreamContent(None, iter([1,2,3]))
        self.assertTrue(isinstance(iter(sc), StreamContent))

    def test_next_no_header(self):
        sc = StreamContent(None, iter([1,2,3]))
        content = [ item for item in sc ]
        self.assertListEqual([1,2,3], content)


    def test_next_header(self):
        sc = StreamContent("header", iter([1,2,3]))
        content = [ item for item in sc ]
        self.assertListEqual(["header",1,2,3], content)
