from unittest.mock import patch

from django.core.signing import TimestampSigner
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase


class TempDownloadLinkTests(APITestCase):
    def setUp(self):
        self.signer = TimestampSigner()

    def test_temp_download_link_returns_token_url(self):
        response = self.client.get(reverse("complaint_search:temp_link"))

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        text = response.content.decode()
        self.assertIn("/download/", text)

        token = text.split("/download/")[1].strip("/")
        unsigned = self.signer.unsign(token)
        self.assertEqual(unsigned, "")


class DownloadWithTokenTests(APITestCase):
    def setUp(self):
        self.signer = TimestampSigner()

    def test_download_with_valid_token(self):
        token = self.signer.sign("")
        url = reverse("complaint_search:download", kwargs={"token": token})

        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.content.decode().startswith("https://"))

    def test_download_with_expired_token(self):
        with patch('time.time', return_value=1000.0):
            token = self.signer.sign("")

        with patch('time.time', return_value=1100.0):
            url = reverse("complaint_search:download", kwargs={"token": token})

            response = self.client.get(url)

            self.assertEqual(response.status_code, 410)
            self.assertIn("expired", response.content.decode().lower())

    def test_download_with_invalid_token(self):
        invalid_token = "not-a-real-token"
        url = reverse("complaint_search:download", kwargs={"token": invalid_token})

        response = self.client.get(url)

        self.assertEqual(response.status_code, 400)
        self.assertIn("invalid", response.content.decode().lower())
