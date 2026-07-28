import csv
import json
import os
import shutil
import zipfile
from csv import DictWriter

from django.http import FileResponse

from complaint_search.export_temp import (
    create_export_temp_dir,
    sweep_export_temp_files,
)


class TempZipFileResponse(FileResponse):
    """Serve a zip file from disk and remove its temp directory when done."""

    def __init__(self, zip_path, temp_dir):
        self._temp_dir = temp_dir
        self._zip_path = zip_path
        super().__init__(open(zip_path, "rb"), content_type="application/zip")

    def close(self):
        super().close()
        shutil.rmtree(self._temp_dir, ignore_errors=True)


class OpenSearchExporter(object):

    def _export_zip(self, data_filename, write_data):
        sweep_export_temp_files()
        temp_dir = create_export_temp_dir()
        data_path = os.path.join(temp_dir, data_filename)
        zip_path = os.path.join(temp_dir, "export.zip")
        try:
            write_data(data_path)
            with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
                zf.write(data_path, arcname=data_filename)
            os.remove(data_path)
            response = TempZipFileResponse(zip_path, temp_dir)
            response["Content-Disposition"] = 'attachment; filename="export.zip"'
            return response
        except Exception:
            shutil.rmtree(temp_dir, ignore_errors=True)
            raise

    # export_csv - Export an OpenSearch response as a CSV file inside a zip
    #
    # Parameters:
    # - scanResponse (generator)
    #   The response from an OpenSearch scan query
    # - header_dict (OrderedDict)
    #   The ordered dictionary where the key is the OpenSearch field name
    #   and the value is the CSV column header for that field
    def export_csv(self, scanResponse, header_dict):
        def write_data(data_path):
            with open(data_path, "w", newline="", encoding="utf-8") as csv_file:
                writer = DictWriter(
                    csv_file,
                    header_dict.keys(),
                    delimiter=",",
                    quoting=csv.QUOTE_MINIMAL,
                )
                writer.writerow(header_dict)
                for row in scanResponse:
                    rows_data = {
                        key: str(value)
                        for key, value in row["_source"].items()
                        if key in header_dict.keys()
                    }
                    writer.writerow(rows_data)

        return self._export_zip("complaints.csv", write_data)

    # export_json - Export an OpenSearch response as a JSON file inside a zip
    #
    # Parameters:
    # - scanResponse (generator)
    #   The response from an OpenSearch scan query
    # - total_count (int)
    #   The total number of records to be output
    def export_json(self, scanResponse, total_count):
        def write_data(data_path):
            with open(data_path, "w", encoding="utf-8") as json_file:
                json_file.write("[")
                count = 0
                for row in scanResponse:
                    count += 1
                    if count < total_count:
                        json_file.write("{},".format(json.dumps(row)))
                    else:
                        json_file.write(json.dumps(row))
                json_file.write("]")

        return self._export_zip("complaints.json", write_data)
