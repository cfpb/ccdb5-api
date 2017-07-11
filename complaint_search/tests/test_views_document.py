from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from unittest import skip
from elasticsearch import TransportError
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

    @mock.patch('complaint_search.es_interface.document')
    def test_document__transport_error_with_status_code(self, mock_esdocument):
        mock_esdocument.side_effect = TransportError(status.HTTP_404_NOT_FOUND, "Error")
        url = reverse('complaint_search:document', kwargs={"id": "123456"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertDictEqual({"error": "Elasticsearch error: Error"}, response.data)

    @mock.patch('complaint_search.es_interface.document')
    def test_document__transport_error_without_status_code(self, mock_esdocument):
        mock_esdocument.side_effect = TransportError('N/A', "Error")
        url = reverse('complaint_search:document', kwargs={"id": "123456"})
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertDictEqual({"error": "Elasticsearch error: Error"}, response.data)


