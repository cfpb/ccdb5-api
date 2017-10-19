import StringIO

def update_headers(headers_dict, csv_content):
    string_handle = StringIO.StringIO(csv_content)

    orig_header_list = [ field.strip().replace('"', '') 
        for field in string_handle.readline().split(",") ]
    new_header_list = [ '"' + headers_dict.get(field, field) + '"'
        for field in orig_header_list ]
    print orig_header_list
    print new_header_list
    new_header_row = ",".join(field for field in new_header_list) + "\n"

    new_content = new_header_row + string_handle.read()
    print new_header_row
    print new_content
    return new_content