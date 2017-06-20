# Most of the serializer code has been tested through the views
from django.test import TestCase
from complaint_search.serializer import SearchInputSerializer

class SearchInputSerializerTests(TestCase):

    def setUp(self):
        self.data = {
        }

    def test_is_valid__no_args(self):
        serializer = SearchInputSerializer(data={})
        self.assertTrue(serializer.is_valid())
        self.assertEqual({}, serializer.validated_data)

    def test_is_valid__valid_product(self):
        self.data['product'] = [u"Mortgage\u2022FHA Mortgage", "Payday Loan"]
        serializer = SearchInputSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_is_valid__invalid_product(self):
        self.data['product'] = [u"Mortgage\u2022FHA Mortgage", "Payday Loan", u"Test\u2022Test\u2022"]
        serializer = SearchInputSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('product'), [u'Product is malformed, it needs to be "product" or "product\u2022subproduct"'])

    def test_is_valid__valid_issue(self):
        self.data['issue'] = [u"Test Issue\u2022Sub issue", "Issue 2"]
        serializer = SearchInputSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_is_valid__invalid_issue(self):
        self.data['issue'] = [u"Test Issue\u2022Sub issue", "Issue 2", u"Test\u2022Test\u2022"]
        serializer = SearchInputSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(serializer.errors.get('issue'), [u'Issue is malformed, it needs to be "issue" or "issue\u2022subissue"'])




