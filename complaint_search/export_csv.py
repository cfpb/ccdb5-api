import json
import os
import sys
import csv
import elasticsearch
from elasticsearch import helpers
from elasticsearch import Elasticsearch
from collections import OrderedDict

from django.http import StreamingHttpResponse

import cStringIO as StringIO
import csv

# make sure no encode issues
reload(sys)
sys.setdefaultencoding('utf8')

class ElasticSearchExporter(object):

    # export_1 - query Elasticsearch and stream the response as a CSV
    #
    # Parameters:
    # - es (Elasticsearch instance)
    #   The Elasticsearch instance to query against
    # - index (string)
    #   The Elasticsearch index to query against
    # - doc_type (string)
    #   The document type in the desired index
    # - body (string)
    #   The body of the Elasticsearch query
    # - header_dict (OrderedDict)
    #   The ordered dictionary where the key is the Elasticsearch field name
    #   and the value is the CSV column header for that field 
    def export_1(self, es, index, doc_type, body, header_dict):
        def read_and_flush(writer, buffer_, row):
            writer.writerow(row)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            return data

        def stream():
            buffer_ = StringIO.StringIO()
            writer = csv.DictWriter(buffer_, header_dict.keys(), 
                delimiter=",",quoting=csv.QUOTE_MINIMAL)

            scanResponse = helpers.scan(client=es, query=body, scroll= "10m", 
                index=index, size=body["size"], doc_type=doc_type, 
                request_timeout=3000)
            
            # Write Header Row
            data = read_and_flush(writer, buffer_, header_dict)
            yield data

            # Write CSV
            for row in scanResponse:
                rows_data = {key: unicode(value) for key, value in row['_source'].iteritems()
                             if key in header_dict.keys()}

                data = read_and_flush(writer, buffer_, rows_data)
                yield data

        response = StreamingHttpResponse(
            stream(), content_type='text/csv'
        )
        response['Content-Disposition'] = "attachment; filename=file.csv"
        return response


    # export_2 - Stream an Elsticsearch response as a CSV
    #
    # Parameters:
    # - scanResponse (generator)
    #   The response from an Elasticsaerch scan query
    # - header_dict (OrderedDict)
    #   The ordered dictionary where the key is the Elasticsearch field name
    #   and the value is the CSV column header for that field 
    def export_2(self, scanResponse, header_dict):
        def read_and_flush(writer, buffer_, row):
            writer.writerow(row)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            return data

        def stream():
            buffer_ = StringIO.StringIO()
            writer = csv.DictWriter(buffer_, header_dict.keys(), 
                delimiter=",",quoting=csv.QUOTE_MINIMAL)
            
            # Write Header Row
            data = read_and_flush(writer, buffer_, header_dict)
            yield data

            # Write CSV
            for row in scanResponse:
                rows_data = {key: unicode(value) for key, value in row['_source'].iteritems()
                             if key in header_dict.keys()}

                data = read_and_flush(writer, buffer_, rows_data)
                yield data

        response = StreamingHttpResponse(
            stream(), content_type='text/csv'
        )
        response['Content-Disposition'] = "attachment; filename=file.csv"
        return response

