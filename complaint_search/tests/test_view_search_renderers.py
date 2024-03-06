from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase


try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


DEFAULT_ACCEPT = (
    "text/html,application/xhtml+xml,application/xml;q=0.9,"
    "image/webp,image/apng,*/*;q=0.8"
)


class SearchRendererTests(APITestCase):
    @mock.patch("complaint_search.es_interface.search")
    def test_search_no_format_chrome_request(self, mock_essearch):
        expected = {"foo": "bar"}
        mock_essearch.return_value = expected

        url = reverse("complaint_search:search")
        response = self.client.get(url, HTTP_ACCEPT=DEFAULT_ACCEPT)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(expected, response.data)
        self.assertEqual(response["Content-Type"], "application/json")

    @mock.patch("complaint_search.es_interface.search")
    def test_search_accept_html_only(self, mock_essearch):
        expected = {"foo": "bar"}
        mock_essearch.return_value = expected
        accept = "text/html"

        url = reverse("complaint_search:search")
        response = self.client.get(url, HTTP_ACCEPT=accept)
        self.assertEqual(response.status_code, 406)
        self.assertEqual(response["Content-Type"], "application/json")
