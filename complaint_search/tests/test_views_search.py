from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest import skip
import mock
from complaint_search.es_interface import search

class SearchTests(APITestCase):

    def setUp(self):
        pass

    @mock.patch('complaint_search.es_interface.search')
    def test_search_no_param(self, mock_essearch):
        """
        Searching with no parameters
        """
        url = reverse('complaint_search:search')
        mock_essearch.return_value = 'OK'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_essearch.assert_called_once_with()
        self.assertEqual('OK', response.data)
