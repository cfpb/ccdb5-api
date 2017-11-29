from django.core.urlresolvers import reverse
from rest_framework import status
from rest_framework.test import APITestCase
import io


class SwaggerTests(APITestCase):
    def test_provide(self):
        url = reverse('complaint_search:swagger')

        response = self.client.get(url)
        data = ''.join([l for l in response.streaming_content])

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual('swagger', data[:7])
