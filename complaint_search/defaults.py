PARAMS = {
    "format": "default", 
    "field": "complaint_what_happened", 
    "size": 10, 
    "frm": 0,
    "sort": "relevance_desc",
    "no_aggs": False,
    "no_highlight": False,
}

# -*- coding: utf-8 -*-
DELIMITER = u'\u2022'

SOURCE_FIELDS = (
    "sub_product",
    "date_sent_to_company",
    "complaint_id",
    "consumer_consent_provided",
    "date_received",
    "state",
    "issue",
    "company_response",
    "zip_code",
    "timely",
    "product",
    "complaint_what_happened",
    "company",
    "sub_issue",
    "tags",
    "company_public_response",
    "consumer_disputed",
    "has_narrative",
    "submitted_via",
)

EXPORT_FORMATS = (
    'json',
    'csv',
)