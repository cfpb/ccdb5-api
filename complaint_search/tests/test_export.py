#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
from collections import OrderedDict

from django.http import StreamingHttpResponse
from django.test import TestCase

from parameterized import parameterized

from complaint_search.export import ElasticSearchExporter


TEST_HEADERS = OrderedDict(
    [
        ("first_entry", "First Entry"),
        ("second_entry", "Second Entry"),
        ("third_entry", "Third Entry"),
        ("fourth_entry", "Fourth Entry"),
    ]
)


def es_generator(n):
    count = 0
    while count < n:
        yield {
            "_source": {
                "first_entry": "Random 1",
                "second_entry": "Random 2",
                "third_entry": "Random 3",
                "fourth_entry": "Random 4",
            }
        }
        count += 1


class ExportTest(TestCase):
    @parameterized.expand([[10], [5010], [100000]])
    def test_export_csv_request_response(self, length):
        # arrange
        es_exporter = ElasticSearchExporter()
        gen = es_generator(length)

        # act
        res = es_exporter.export_csv(gen, TEST_HEADERS)

        # assert
        self.assertTrue(isinstance(res, StreamingHttpResponse))

        # mock_search.assert_not_called()
        self.assertEqual(
            res.get("Content-Disposition"), "attachment; filename=file.csv"
        )
        self.assertTrue("map" in str(type(res.streaming_content)))
        downloaded_file = io.BytesIO(b"".join(res.streaming_content))
        self.assertFalse(downloaded_file is None)

    @parameterized.expand([[10], [5010], [100000]])
    def test_export_json_request_response(self, length):
        # arrange
        es_exporter = ElasticSearchExporter()
        gen = es_generator(length)

        # act
        res = es_exporter.export_json(gen, length)

        # assert
        self.assertTrue(isinstance(res, StreamingHttpResponse))

        # mock_search.assert_not_called()
        self.assertEqual(
            res.get("Content-Disposition"), "attachment; filename=file.json"
        )
        self.assertTrue("map" in str(type(res.streaming_content)))
        downloaded_file = io.BytesIO(b"".join(res.streaming_content))
        self.assertFalse(downloaded_file is None)


class TestCSVExportWithUnicodeCharacters(TestCase):
    def test_export_contains_unicode_chacter(self):
        headers = OrderedDict(
            [
                ("key", "Key"),
            ]
        )

        def unicode_results():
            yield {
                "_source": {
                    "key": "\u2019",
                },
            }

        exporter = ElasticSearchExporter()
        response = exporter.export_csv(unicode_results(), headers)
        content = io.BytesIO(b"".join(response.streaming_content)).read()
        self.assertEqual(content, b"Key\r\n\xe2\x80\x99\r\n")
