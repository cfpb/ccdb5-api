from django.test import TestCase

from complaint_search.stream_content import StreamCSVContent, StreamJSONContent


class StreamCSVContentTests(TestCase):
    def setUp(self):
        pass

    def test_iter(self):
        sc = StreamCSVContent(None, iter([1, 2, 3]))
        self.assertTrue(isinstance(iter(sc), StreamCSVContent))

    def test_next_no_header(self):
        sc = StreamCSVContent(None, iter([1, 2, 3]))
        content = [item for item in sc]
        self.assertListEqual([1, 2, 3], content)

    def test_next_header(self):
        sc = StreamCSVContent("header", iter([1, 2, 3]))
        content = [item for item in sc]
        self.assertListEqual(["header", 1, 2, 3], content)


class StreamJSONContentTests(TestCase):
    def setUp(self):
        self.content = (
            '{"index": {"_index": "test", "_id": 12345}}\n'
            '{"product": "mortgage", "complaint_id": 12345, "tags": null}\n'
            '{"index": {"_index": "test", "_id": 23456}}\n'
            '{"product": "test", "complaint_id": 23456, '
            '"tags": "Older Americans"}\n'
            '{"index": {"_index": "test", "_id": 45678}}\n'
            '{"product": "loan", "complaint_id": 45678, "tags": null} \n'
        )

        # pretend this is broken up randomly every 20 chars
        self.content_list = [
            self.content[(i * 20) : (i * 20 + 20)]
            for i in range(int(len(self.content) / 20 + 1))
        ]

    def test_iter(self):
        sc = StreamJSONContent(iter(self.content_list))
        self.assertTrue(isinstance(iter(sc), StreamJSONContent))

    def test_next_complete(self):
        for size in range(1, 1024):
            content_list = [
                self.content[(i * size) : (i * size + size)]
                for i in range(int(len(self.content) / size + 1))
            ]
            sc = StreamJSONContent(iter(content_list))
            result = ""
            for json_in_progress in sc:
                result += json_in_progress

            exp_result = (
                '[{"product": "mortgage", "complaint_id": 12345, '
                '"tags": null},'
                '{"product": "test", "complaint_id": 23456, '
                '"tags": "Older Americans"},'
                '{"product": "loan", "complaint_id": 45678, "tags": null}]'
            )
            self.assertEqual(exp_result, result)
