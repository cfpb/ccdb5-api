from django.core.urlresolvers import reverse
from django.conf import settings
from rest_framework import status
from rest_framework.test import APITestCase
from unittest import skip
import mock
from datetime import date
from complaint_search.es_interface import search
from complaint_search.serializer import SearchInputSerializer

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

    @mock.patch('complaint_search.es_interface.search')
    def test_search_cors_headers(self, mock_essearch):
        """
        Make sure the response has CORS headers in debug mode
        """
        settings.DEBUG = True
        url = reverse('complaint_search:search')
        mock_essearch.return_value = 'OK'
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.has_header('Access-Control-Allow-Origin'))

    # @mock.patch('complaint_search.es_interface.search')
    # def test_search_with_fmt(self, mock_essearch):
    #     """
    #     Searching with fmt
    #     """
    #     url = reverse('complaint_search:search')
    #     params = {"test": "fowrawe", "erara": "earea"}
    #     mock_essearch.return_value = 'OK'
    #     response = self.client.get(url, params)
    #     self.assertEqual(response.status_code, status.HTTP_200_OK)
    #     mock_essearch.assert_called_once_with()
    #     self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_field__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        for field in SearchInputSerializer.FIELD_CHOICES:
            params = {"field": field[0]}
            mock_essearch.return_value = 'OK'
            response = self.client.get(url, params)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual('OK', response.data)

        calls = [ mock.call(
            **{"field": SearchInputSerializer.FIELD_MAP.get(field_pair[0], 
                field_pair[0])}) 
                for field_pair in SearchInputSerializer.FIELD_CHOICES ]
        mock_essearch.assert_has_calls(calls)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_field__invalid_choice(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"field": "invalid_choice"}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_essearch.assert_not_called()
        self.assertDictEqual({"field": ["\"invalid_choice\" is not a valid choice."]}, 
            response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_size__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"size": 4}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        mock_essearch.assert_called_once_with(**{"size": 4})
        self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_size__invalid_type(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"size": "not_integer"}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_essearch.assert_not_called()
        self.assertDictEqual({"size": ["A valid integer is required."]}, 
            response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_size__invalid_smaller_than_min_number(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"size": -1}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_essearch.assert_not_called()
        self.assertDictEqual(
            {"size": ["Ensure this value is greater than or equal to 1."]}, 
            response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_size__invalid_exceed_max_number(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"size": 100001}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_essearch.assert_not_called()
        self.assertDictEqual(
            {"size": ["Ensure this value is less than or equal to 100000."]}, 
            response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_frm__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"frm": 4}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        mock_essearch.assert_called_once_with(**{"frm": 4})
        self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_frm__invalid_type(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"frm": "not_integer"}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_essearch.assert_not_called()
        self.assertDictEqual({"frm": ["A valid integer is required."]}, 
            response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_frm__invalid_smaller_than_min_number(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"frm": -1}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_essearch.assert_not_called()
        self.assertDictEqual(
            {"frm": ["Ensure this value is greater than or equal to 0."]}, 
            response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_frm__invalid_exceed_max_number(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"frm": 100001}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_essearch.assert_not_called()
        self.assertDictEqual(
            {"frm": ["Ensure this value is less than or equal to 100000."]}, 
            response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_sort__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        for sort in SearchInputSerializer.SORT_CHOICES:
            params = {"sort": sort[0]}
            mock_essearch.return_value = 'OK'
            response = self.client.get(url, params)
            self.assertEqual(status.HTTP_200_OK, response.status_code)
            self.assertEqual('OK', response.data)

        calls = [ mock.call(**{"sort": sort_pair[0]}) 
            for sort_pair in SearchInputSerializer.SORT_CHOICES ]
        mock_essearch.assert_has_calls(calls)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_sort__invalid_choice(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"sort": "invalid_choice"}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_essearch.assert_not_called()
        self.assertDictEqual({"sort": ["\"invalid_choice\" is not a valid choice."]}, 
            response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_search_term__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"search_term": "FHA Mortgage"}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        mock_essearch.assert_called_once_with(**params)
        self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_min_date__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"min_date": "2017-04-11"}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        mock_essearch.assert_called_once_with(**{"min_date": date(2017, 04, 11)})
        self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_min_date__invalid_format(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"min_date": "not_a_date"}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_essearch.assert_not_called()
        self.assertDictEqual({"min_date": ["Date has wrong format. Use one of these formats instead: YYYY[-MM[-DD]]."]}, 
            response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_max_date__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"max_date": "2017-04-11"}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        mock_essearch.assert_called_once_with(**{"max_date": date(2017, 04, 11)})
        self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_max_date__invalid_format(self, mock_essearch):
        url = reverse('complaint_search:search')
        params = {"max_date": "not_a_date"}
        mock_essearch.return_value = 'OK'
        response = self.client.get(url, params)
        self.assertEqual(status.HTTP_400_BAD_REQUEST, response.status_code)
        mock_essearch.assert_not_called()
        self.assertDictEqual({"max_date": ["Date has wrong format. Use one of these formats instead: YYYY[-MM[-DD]]."]}, 
            response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_company__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        url += "?company=One%20Bank&company=Bank%202"
        mock_essearch.return_value = 'OK'
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        mock_essearch.assert_called_once_with(**{"company": ["One Bank", "Bank 2"]})
        self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_product__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        # parameter doesn't represent real data, as client has a hard time 
        # taking unicode.  The original API will use a bullet u2022 in place 
        # of the '-'
        url += "?product=Mortgage-FHA%20Mortgage&product=Payday%20Loan"
        mock_essearch.return_value = 'OK'
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        mock_essearch.assert_called_once_with(
            **{"product": ["Mortgage-FHA Mortgage", "Payday Loan"]})
        self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_issue__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        # parameter doesn't represent real data, as client has a hard time 
        # taking unicode.  The original API will use a bullet u2022 in place 
        # of the '-'
        url += "?issue=Communication%20tactics-Frequent%20or%20repeated%20calls" \
        "&issue=Loan%20servicing,%20payments,%20escrow%20account"
        mock_essearch.return_value = 'OK'
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # -*- coding: utf-8 -*-
        mock_essearch.assert_called_once_with(
            **{"issue": ["Communication tactics-Frequent or repeated calls", 
            "Loan servicing, payments, escrow account"]})
        self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_state__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        url += "?state=CA&state=FL&state=VA"
        mock_essearch.return_value = 'OK'
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # -*- coding: utf-8 -*-
        mock_essearch.assert_called_once_with(
            **{"state": ["CA", "FL", "VA"]})
        self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_consumer_disputed__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        url += "?consumer_disputed=yes&consumer_disputed=no"
        mock_essearch.return_value = 'OK'
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # -*- coding: utf-8 -*-
        mock_essearch.assert_called_once_with(
            **{"consumer_disputed": ["yes", "no"]})
        self.assertEqual('OK', response.data)

    @mock.patch('complaint_search.es_interface.search')
    def test_search_with_company_response__valid(self, mock_essearch):
        url = reverse('complaint_search:search')
        url += "?company_response=Closed&company_response=No%20response"
        mock_essearch.return_value = 'OK'
        response = self.client.get(url)
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        # -*- coding: utf-8 -*-
        mock_essearch.assert_called_once_with(
            **{"company_response": ["Closed", "No response"]})
        self.assertEqual('OK', response.data)