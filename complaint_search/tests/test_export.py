#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import os
import zipfile
from collections import OrderedDict

from django.test import TestCase

from parameterized import parameterized

from complaint_search.export import OpenSearchExporter, TempZipFileResponse


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


def read_zip_member(response, member_name):
    zip_bytes = b"".join(response)
    response.close()
    with zipfile.ZipFile(io.BytesIO(zip_bytes)) as archive:
        return archive.read(member_name)


class ExportTest(TestCase):
    @parameterized.expand([[10], [5010], [100000]])
    def test_export_csv_request_response(self, length):
        # arrange
        es_exporter = OpenSearchExporter()
        gen = es_generator(length)

        # act
        res = es_exporter.export_csv(gen, TEST_HEADERS)

        # assert
        self.assertTrue(isinstance(res, TempZipFileResponse))
        self.assertEqual(
            res.get("Content-Disposition"), 'attachment; filename="export.zip"'
        )
        self.assertEqual(res.get("Content-Type"), "application/zip")
        csv_content = read_zip_member(res, "complaints.csv")
        self.assertFalse(csv_content is None)
        self.assertFalse(os.path.exists(res._temp_dir))

    @parameterized.expand([[10], [5010], [100000]])
    def test_export_json_request_response(self, length):
        # arrange
        es_exporter = OpenSearchExporter()
        gen = es_generator(length)

        # act
        res = es_exporter.export_json(gen, length)

        # assert
        self.assertTrue(isinstance(res, TempZipFileResponse))
        self.assertEqual(
            res.get("Content-Disposition"), 'attachment; filename="export.zip"'
        )
        self.assertEqual(res.get("Content-Type"), "application/zip")
        json_content = read_zip_member(res, "complaints.json")
        self.assertFalse(json_content is None)
        self.assertFalse(os.path.exists(res._temp_dir))


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

        exporter = OpenSearchExporter()
        response = exporter.export_csv(unicode_results(), headers)
        content = read_zip_member(response, "complaints.csv")
        self.assertEqual(content, b"Key\r\n\xe2\x80\x99\r\n")
