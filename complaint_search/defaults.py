from collections import OrderedDict


# AGG defaults:
# Most of our defaults cover size limits for aggregation buckets.
# Defaults were adjusted in 2021 to be higher than object counts at the time.
# Counts for ZIP Codes and states are unlikely to change much, but others may.
# Companies, products, and issues could grow over time and need adjustment.
AGG_COMPANY_DEFAULT = 6500
AGG_ZIPCODE_DEFAULT = 26000
AGG_STATE_DEFAULT = 100
AGG_STATE_PRODUCT_DEFAULT = 5
AGG_STATE_ISSUE_DEFAULT = 5
AGG_ISSUE_DEFAULT = 200
AGG_SUBISSUE_DEFAULT = 250
AGG_PRODUCT_DEFAULT = 30
AGG_SUBPRODUCT_DEFAULT = 90
# Other defaults:
# Pagination batch is the number of results we paginate at a time.
# Max pagination depth is the farthest we'll paginate – 100 batches.
# The default result size matches the front-end default for users.
# The trend_depth default limits display to 5 items in some Trends contexts.
PAGINATION_BATCH = 100
MAX_PAGINATION_DEPTH = 10000
RESULT_SIZE_DEFAULT = 25
RESULT_SIZE_OPTIONS = [10, 50, 100]
TREND_DEPTH_DEFAULT = 5

PARAMS = {
    "format": "default",
    "field": "complaint_what_happened",
    "frm": 0,
    "search_after": "",
    "page": 1,
    "no_aggs": False,
    "no_highlight": False,
    "size": RESULT_SIZE_DEFAULT,
    "sort": "relevance_desc",
}

# -*- coding: utf-8 -*-
DELIMITER = "\u2022"

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

EXCLUDE_PREFIX = "not_"

EXPORT_FORMATS = (
    "csv",
    "json",
)

CSV_ORDERED_HEADERS = OrderedDict(
    [
        ("date_received_formatted", "Date received"),
        ("product", "Product"),
        ("sub_product", "Sub-product"),
        ("issue", "Issue"),
        ("sub_issue", "Sub-issue"),
        ("complaint_what_happened", "Consumer complaint narrative"),
        ("company_public_response", "Company public response"),
        ("company", "Company"),
        ("state", "State"),
        ("zip_code", "ZIP code"),
        ("tags", "Tags"),
        ("consumer_consent_provided", "Consumer consent provided?"),
        ("submitted_via", "Submitted via"),
        ("date_sent_to_company_formatted", "Date sent to company"),
        ("company_response", "Company response to consumer"),
        ("timely", "Timely response?"),
        ("consumer_disputed", "Consumer disputed?"),
        ("complaint_id", "Complaint ID"),
    ]
)

AGG_EXCLUDE_FIELDS = ["company", "zip_code"]

CHUNK_SIZE = 512

FORMAT_CONTENT_TYPE_MAP = {
    "json": "application/json",
    "csv": "text/csv",
}

DATA_SUB_LENS_MAP = {
    "product": ("sub_product", "issue", "company", "tags"),
    "issue": ("product", "sub_issue", "company", "tags"),
    "company": ("product", "issue", "tags"),
    "tags": ("product", "issue", "company"),
}
