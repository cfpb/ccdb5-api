from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest import skip
import mock
from complaint_search.es_interface import document

class DocumentTests(APITestCase):

    def setUp(self):
        pass

    @mock.patch('complaint_search.es_interface.document')
    def test_document__valid(self, mock_esdocument):
        """
        documenting with an ID
        """
        url = reverse('complaint_search:document', kwargs={"id": "123456"})
        mock_esdocument.return_value = 'OK'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        mock_esdocument.assert_called_once_with("123456")
        self.assertEqual('OK', response.data)