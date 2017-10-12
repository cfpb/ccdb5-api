PARAMS = {
    "format": "default",
    "field": "complaint_what_happened",
    "frm": 0,
    "no_aggs": False,
    "no_highlight": False,
    "size": 10,
    "sort": "relevance_desc",
}

# -*- coding: utf-8 -*-
DELIMITER = u'\u2022'

SOURCE_FIELDS = (
    "company",
    "company_public_response",
    "company_response",
    "complaint_id",
    "complaint_what_happened",
    "consumer_consent_provided",
    "consumer_disputed",
    "date_received",
    "date_sent_to_company",
    "has_narrative",
    "issue",
    "product",
    "state",
    "submitted_via",
    "sub_issue",
    "sub_product",
    "tags",
    "timely",
    "zip_code",
)

EXPORT_FORMATS = (
    'csv',
    'json',
)