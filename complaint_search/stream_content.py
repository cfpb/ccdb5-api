class StreamCSVContent(object):
    def __init__(self, header, content):
        self.header = header
        self.content = content
        self.is_header_returned = False

    def __iter__(self):
        return self

    def __next__(self):
        if self.header and not self.is_header_returned:
            self.is_header_returned = True
            return self.header
        else:
            return next(self.content)


class StreamJSONContent(object):
    def __init__(self, content):
        self.content = content
        self.complaint_in_progress = ""
        self.is_streaming_started = False
        self.is_streaming_stopped = False

    def get_next_complaint(self):
        self.complaint_in_progress = self.complaint_in_progress.lstrip()
        # see if first line is reached
        try:
            first_eol_index = self.complaint_in_progress.index("\n")

            # see if we have 2nd completed line, and that's the complaint we
            # want to return assuming at the EOF there's also a '\n' as seen
            # from data format plugin so far
            second_eol_index = self.complaint_in_progress.index(
                "\n", first_eol_index + 1
            )

            complaint = self.complaint_in_progress[
                first_eol_index + 1 : second_eol_index + 1
            ].strip()
            # save the rest for next iteration
            self.complaint_in_progress = self.complaint_in_progress[
                second_eol_index + 1 :
            ]
            return complaint
        except ValueError:
            # This means cannot find two \n, complaint is not ready, need more
            # data
            return None

    def __iter__(self):
        return self

    def __next__(self):
        while True:
            if not self.is_streaming_started:
                # This is the beginning
                self.is_streaming_started = True
                return "["
            try:
                next_chunk = next(self.content)
                self.complaint_in_progress += next_chunk
                # peek ahead, it will raise StopIteration if no more chunk
                next2_chunk = next(self.content)
                complaint = self.get_next_complaint()
                self.complaint_in_progress += next2_chunk
                if complaint and self.complaint_in_progress.strip():
                    return complaint + ","
                elif complaint and not self.complaint_in_progress.strip():
                    return complaint
            except StopIteration:
                complaint = self.get_next_complaint()
                if complaint and not self.complaint_in_progress.strip():
                    return complaint
                elif complaint and self.complaint_in_progress.strip():
                    return complaint + ","
                elif not self.is_streaming_stopped:
                    # This is the end
                    self.is_streaming_stopped = True
                    return "]"
                else:
                    raise StopIteration
