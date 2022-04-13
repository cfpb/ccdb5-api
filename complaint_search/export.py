import csv
import json
from csv import DictWriter
from io import StringIO

from django.http import StreamingHttpResponse


class ElasticSearchExporter(object):

    # export_csv - Stream an Elsticsearch response as a CSV file
    #
    # Parameters:
    # - scanResponse (generator)
    #   The response from an Elasticsaerch scan query
    # - header_dict (OrderedDict)
    #   The ordered dictionary where the key is the Elasticsearch field name
    #   and the value is the CSV column header for that field
    def export_csv(self, scanResponse, header_dict):
        def read_and_flush(writer, buffer_, row):
            writer.writerow(row)
            buffer_.seek(0)
            data = buffer_.read()
            buffer_.seek(0)
            buffer_.truncate()
            return data

        def stream():
            buffer_ = StringIO()
            writer = DictWriter(
                buffer_,
                header_dict.keys(),
                delimiter=",",
                quoting=csv.QUOTE_MINIMAL,
            )

            # Write Header Row
            data = read_and_flush(writer, buffer_, header_dict)
            yield data

            count = 0
            # Write CSV
            for row in scanResponse:
                count += 1
                rows_data = {
                    key: str(value)
                    for key, value in row["_source"].items()
                    if key in header_dict.keys()
                }

                data = read_and_flush(writer, buffer_, rows_data)
                yield data

        response = StreamingHttpResponse(stream(), content_type="text/csv")
        response["Content-Disposition"] = "attachment; filename=file.csv"
        return response

    # export_json - Stream an Elsticsearch response as a JSON file
    #
    # Parameters:
    # - scanResponse (generator)
    #   The response from an Elasticsearch scan query
    # - total_count (int)
    #   The total number of records to be output
    def export_json(self, scanResponse, total_count):
        def stream():
            count = 0
            # Write JSON
            yield "["
            for row in scanResponse:
                count += 1
                if count < total_count:
                    yield "{},".format(json.dumps(row))
                else:
                    yield json.dumps(row)

            yield "]"

        response = StreamingHttpResponse(stream(), content_type="text/json")
        response["Content-Disposition"] = "attachment; filename=file.json"
        return response
