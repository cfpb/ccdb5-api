from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest import skip
import mock
from complaint_search.es_interface import suggest

class SuggestTests(APITestCase):

    def setUp(self):
        pass

    @mock.patch('complaint_search.es_interface.suggest')
    def test_suggest_no_param(self, mock_essuggest):
        """
        Suggesting with no parameters
        """
        url = reverse('complaint_search:suggest')
        mock_essuggest.return_value = 'OK'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_essuggest.assert_called_once_with()
        self.assertEqual('OK', response.data)
