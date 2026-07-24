from django.test import RequestFactory, TestCase

from opensearchpy import ConnectionTimeout, TransportError
from rest_framework import status
from rest_framework.exceptions import ValidationError

from complaint_search.decorators import catch_es_error


class CatchESErrorTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")

    def test_api_exception_is_not_swallowed(self):
        @catch_es_error
        def view(request):
            raise ValidationError({"size": ["too big"]})

        with self.assertRaises(ValidationError):
            view(self.request)

    def test_transport_error_returns_424(self):
        @catch_es_error
        def view(request):
            raise TransportError(503, "unavailable", {})

        with self.assertLogs("complaint_search.decorators", "ERROR") as logs:
            response = view(self.request)

        self.assertEqual(response.status_code, 424)
        self.assertIn("OpenSearch TransportError on /", logs.output[0])

    def test_connection_timeout_is_logged_by_class(self):
        @catch_es_error
        def view(request):
            raise ConnectionTimeout(
                "TIMEOUT", "read timed out", Exception("read timed out")
            )

        with self.assertLogs("complaint_search.decorators", "ERROR") as logs:
            response = view(self.request)

        self.assertEqual(response.status_code, 424)
        self.assertIn("OpenSearch ConnectionTimeout on /", logs.output[0])

    def test_other_errors_return_500_with_traceback(self):
        @catch_es_error
        def view(request):
            raise ValueError

        with self.assertLogs("complaint_search.decorators", "ERROR") as logs:
            response = view(self.request)

        self.assertEqual(response.status_code, status.HTTP_500_INTERNAL_SERVER_ERROR)
        self.assertIn("Traceback", logs.output[0])
