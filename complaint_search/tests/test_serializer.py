# Most of the serializer code has been tested through the views
import copy

from django.test import TestCase

from complaint_search.defaults import PARAMS
from complaint_search.serializer import (
    SearchInputSerializer,
    TrendsInputSerializer,
)


class SearchInputSerializerTests(TestCase):
    def setUp(self):
        self.data = {}

    def test_is_valid__no_args(self):
        serializer = SearchInputSerializer(data={})
        self.assertTrue(serializer.is_valid())

        exp_dict = copy.deepcopy(PARAMS)

        # This is an OrderedDict
        for k, v in serializer.validated_data.items():

            self.assertIn(k, exp_dict)
            self.assertEqual(v, exp_dict[k])

    def test_is_valid__valid_product(self):
        self.data["product"] = ["Mortgage\u2022FHA Mortgage", "Payday Loan"]
        serializer = SearchInputSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_is_valid__invalid_product(self):
        self.data["product"] = [
            "Mortgage\u2022FHA Mortgage",
            "Payday Loan",
            "Test\u2022Test\u2022",
        ]
        serializer = SearchInputSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors.get("product"),
            [
                'Product is malformed, it needs to be "product" or '
                '"product\u2022subproduct"'
            ],
        )

    def test_is_valid__valid_issue(self):
        self.data["issue"] = ["Test Issue\u2022Sub issue", "Issue 2"]
        serializer = SearchInputSerializer(data=self.data)
        self.assertTrue(serializer.is_valid())

    def test_is_valid__invalid_issue(self):
        self.data["issue"] = [
            "Test Issue\u2022Sub issue",
            "Issue 2",
            "Test\u2022Test\u2022",
        ]
        serializer = SearchInputSerializer(data=self.data)
        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors.get("issue"),
            [
                'Issue is malformed, it needs to be "issue" or '
                '"issue\u2022subissue"'
            ],
        )


class TrendsInputSerializerTests(TestCase):
    def setUp(self):
        self.data = {}

    def test_is_valid___no_required_params(self):
        serializer = TrendsInputSerializer(data={})

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["trend_interval"], ["This field is required."]
        )

    def test_is_valid__default_requred_params(self):
        serializer = TrendsInputSerializer(
            data={"trend_interval": "month", "lens": "overview"}
        )

        self.assertTrue(serializer.is_valid())

    def test_is_valid__invalid_lens(self):
        serializer = TrendsInputSerializer(
            data={"trend_interval": "year", "lens": "foo"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["lens"], ['"foo" is not a valid choice.']
        )

    def test_is_valid__valid_lens(self):
        serializer = TrendsInputSerializer(
            data={"trend_interval": "year", "lens": "overview"}
        )

        self.assertTrue(serializer.is_valid())

    def test_is_valid__no_sub_lens(self):
        serializer = TrendsInputSerializer(
            data={"trend_interval": "year", "lens": "product"}
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["non_field_errors"],
            [
                "Either Focus or Sub-lens is required for lens 'product'."
                " Valid sub-lens are: ('sub_product', 'issue', 'company', 'tags')"
            ],
        )

    def test_is_valid__invalid_sub_lens(self):
        serializer = TrendsInputSerializer(
            data={
                "trend_interval": "year",
                "lens": "product",
                "sub_lens": "foobar",
            }
        )

        self.assertFalse(serializer.is_valid())
        self.assertEqual(
            serializer.errors["non_field_errors"],
            [
                "'foobar' is not a valid sub-lens for 'product'. Valid "
                "sub-lens are: ('sub_product', 'issue', 'company', 'tags')"
            ],
        )

    def test_is_valid__valid_sub_lens(self):
        serializer = TrendsInputSerializer(
            data={
                "trend_interval": "year",
                "lens": "product",
                "sub_lens": "company",
            }
        )

        self.assertTrue(serializer.is_valid())

    def test_is_valid__valid_focus(self):
        serializer = TrendsInputSerializer(
            data={
                "trend_interval": "year",
                "lens": "product",
                "focus": "Debt collection",
            }
        )

        self.assertTrue(serializer.is_valid())
