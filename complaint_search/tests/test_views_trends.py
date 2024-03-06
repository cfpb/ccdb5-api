import copy
from unittest import mock

from rest_framework import status
from rest_framework.test import APITestCase

from complaint_search.defaults import PARAMS


try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


class TrendsTests(APITestCase):
    def setUp(self):
        pass

    def buildDefaultParams(self, overrides):
        params = copy.deepcopy(PARAMS)
        params.update(overrides)
        return params

    @mock.patch("complaint_search.es_interface.trends")
    def test_trends_no_required_params__fails(self, mock_essearch):
        """
        Searching with no parameters
        """
        url = reverse("complaint_search:trends")
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_essearch.assert_not_called()

    @mock.patch("complaint_search.es_interface.trends")
    def test_trends_default_params__fails(self, mock_essearch):
        """
        Searching with no required trends parameters
        """
        url = reverse("complaint_search:trends")
        response = self.client.get(url, **self.buildDefaultParams({}))
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_essearch.assert_not_called()

    @mock.patch("complaint_search.es_interface.trends")
    def test_trends_invalid_params__fails(self, mock_essearch):
        """
        Searching with invalid required trends parameters
        """
        url = reverse("complaint_search:trends")
        params = {"lens": "foo"}
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        mock_essearch.assert_not_called()
        self.assertTrue("lens" in response.data.keys())
        self.assertTrue("trend_interval" in response.data.keys())

    @mock.patch("complaint_search.es_interface.trends")
    def test_trends_default_params__passes(self, mock_essearch):
        """
        Searching with default but valid required trends parameters
        """
        url = reverse("complaint_search:trends")
        params = {"lens": "overview", "trend_interval": "month"}

        mock_essearch.return_value = "results"
        response = self.client.get(url, params)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_essearch.assert_called_once()
