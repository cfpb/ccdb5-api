#!/usr/local/bin/python
# coding: utf-8

from rest_framework import status
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from rest_framework.response import Response
from django.http import HttpResponse
from django.conf import settings
from datetime import datetime
from elasticsearch import TransportError
import es_interface
from complaint_search.renderers import CSVRenderer, XLSRenderer, XLSXRenderer
from complaint_search.decorators import catch_es_error
from complaint_search.serializer import SearchInputSerializer, SuggestInputSerializer


@api_view(['GET'])
@renderer_classes((JSONRenderer, CSVRenderer, XLSRenderer, XLSXRenderer, BrowsableAPIRenderer))
@catch_es_error
def search(request):
    """
    Search through everything in Consumer Complaints
    ---
    path: "/"
    parameters:
        - name: format
          in: query
          description: Format to be returned
          required: false
          type: string
          enum:
            - json
            - csv
            - xls
            - xlsx
          default: json
          collectionFormat: multi
        - name: field
          in: query
          description: Search by particular field
          required: false
          type: array
          items:
          type: string
          enum:
            - complaint_what_happened
            - company_public_response
            - all
          default: all
          collectionFormat: multi
        - name: size
          in: query
          description: Limit the size of the search result
          required: false
          type: integer
          maximum: 100000
          minimum: 1
          format: int64
        - name: from
          in: query
          description: Return results starting from a specific index
          required: false
          type: integer
          maximum: 100000
          minimum: 1
          format: int64
        - name: sort
          in: query
          description: Return results sort in a particular order
          required: false
          type: string
          enum:
            - "-relevance"
            - "+relevance"
            - "-created_date"
            - "+created_date"
          default: "-relevance"
        - name: search_term
          in: query
          description: Return results containing specific term
          required: false
          type: string
        - name: min_date
          in: query
          description: Return results with date >= min_date (i.e. 2017-03-04)
          required: false
          type: string
          format: date
        - name: max_date
          in: query
          description: Return results with date < max_date (i.e. 2017-03-04)
          required: false
          type: string
          format: date
        - name: company
          in: query
          description: Filter the results to only return these companies
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi
        - name: product
          in: query
          description: "Filter the results to only return these types of product and subproduct, i.e. product-only: Mortgage, subproduct needs to include product, separated by '•', U+2022: Mortgage•FHA mortgage"
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi
        - name: issue
          in: query
          description: "Filter the results to only return these types of issue and subissue, i.e. product-only: Getting a Loan, subproduct needs to include product, separated by '•', U+2022: Getting a Loan•Can't qualify for a loan"
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi
        - name: state
          in: query
          description: Filter the results to only return these states (use abbreviation, i.e. CA, VA)
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi
        - name: consumer_disputed
          in: query
          description: Filter the results to only return the specified state of consumer disputed, i.e. yes, no
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi
        - name: company_response
          in: query
          description: Filter the results to only return these types of response by the company
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi
        - name: company_public_response
          in: query
          description: Filter the results to only return these types of public response by the company
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi
        - name: consumer_consent_provided
          in: query
          description: Filter the results to only return these types of consent consumer provided
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi
        - name: submitted_via
          in: query
          description: Filter the results to only return these types of way consumers submitted their complaints
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi
        - name: tag
          in: query
          description: Filter the results to only return these types of tag
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi
        - name: has_narratives
          in: query
          description: Filter the results to only return the specified state of whether it has narrative in the complaint or not, i.e. yes, no
          required: false
          type: array
          items: 
          type: string
          collectionFormat: multi

    type:
        results_array:
            required: True
            type: array
            items:
              $ref: '#/definitions/Complaint'

    many: True

    responseMessages:
        - code: 200
          message: "Successful Operation"
        - code: 400
          message: "Invalid status value"

    consumes:
        - application/json
        - application/xml

    produces:
        - "application/json"
        - "text/csv"
        - "application/vnd.ms-excel"
        - "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    """
    fixed_qparam = request.query_params
    QPARAMS_VARS = ('fmt', 'field', 'size', 'frm', 'sort', 
        'search_term', 'min_date', 'max_date')

    QPARAMS_LISTS = ('company', 'product', 'issue', 'state', 
        'zip_code', 'timely', 'consumer_disputed', 'company_response',
        'company_public_response', 'consumer_consent_provided', 
        'has_narratives', 'submitted_via', 'tag')

    # This works too but it may be harder to read
    # data = { param: request.query_params.get(param) 
    #     if param in QPARAMS_VARS else request.query_params.getlist(param)
    #     for param in request.query_params if param in QPARAMS_VARS + QPARAMS_LISTS}

    data = {}

    # Add format to data (only checking if it is csv, xls, xlsx, then specific them)
    format = request.accepted_renderer.format
    if format and format in ('csv', 'xls', 'xlsx'):
        data['format'] = format

    for param in request.query_params:
        if param in QPARAMS_VARS:
            data[param] = request.query_params.get(param) 
        elif param in QPARAMS_LISTS:
            data[param] = request.query_params.getlist(param)
          # TODO: else: Error if extra parameters? Or ignore?

    serializer = SearchInputSerializer(data=data)

    if serializer.is_valid():
        results = es_interface.search(**serializer.validated_data)

        # Local development requires CORS support
        headers = {}
        if settings.DEBUG:
            headers = {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,Authorization',
                'Access-Control-Allow-Methods': 'GET'
            }

        # If format is in csv, xls, xlsx, update its attachment response 
        # with a filename
        if format in ('csv', 'xls', 'xlsx'):
            filename = 'complaints-{}.{}'.format(
                datetime.now().strftime('%Y-%m-%d_%H_%M'), format)
            headers['Content-Disposition'] = 'attachment; filename="{}"'.format(filename)

        return Response(results, headers=headers)

    else:
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@catch_es_error
def suggest(request):
    """
    Autocomplete for the Search of consumer complaints
    ---
    parameters:
        - name: size
          in: query
          description: number of suggestions to return, default 6
          required: true
          type: integer
        - name: text
          in: query
          description: text to find suggestions on
          required: true
          type: string

    type:
        suggest_array:
            required: True
            type: array
            items:
                type: string

    many: True

    responseMessages:
        - code: 200
          message: "Successful Operation"
        - code: 400
          message: "Invalid input"

    consumes:
        - application/json
        - application/xml

    produces:
        - application/json
    """
    QPARAMS_VARS = ("text", "size")
    data = { k:v for k,v in request.query_params.iteritems() if k in QPARAMS_VARS }
    serializer = SuggestInputSerializer(data=data)
    if serializer.is_valid():
        results = es_interface.suggest(**serializer.validated_data)
        return Response(results)
    else:
        return Response(serializer.errors,
            status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@catch_es_error
def document(request, id):
    """
    Find comsumer complaint by ID
    ---
    parameters:
        - name: id
          in: path
          description: ID of the complaint
          required: true
          type: integer
          maximum: 9999999999
          minimum: 0
          format: int64

    responseMessages:
        - code: 200
          message: "Successful Operation"
        - code: 400
          message: "Invalid input"
    """
    results = es_interface.document(id)
    return Response(results)
