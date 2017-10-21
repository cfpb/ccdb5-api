class StreamContent(object):
    def __init__(self, header, content):
        self.header = header
        self.content = content
        self.is_header_returned = False

    def __iter__(self):
        return self

    def next(self):
        if self.header and not self.is_header_returned:
            self.is_header_returned = True
            return self.header
        else:
            return next(self.content)