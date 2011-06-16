class Message():
    def __init__(self, proto, vrs, msg_name):
        self.header = []
        self.ie = []
        self.protocol = proto
        self.version = vrs
        self.message_name = msg_name

        if self.protocol:
            self._add_header_schema()

    def _add_header_schema(self):
        headers = __import__("rammbock.protocols."+self.protocol+"."+self.version, fromlist= ['kekkonen'])
        self.header = headers.message_headers[self.message_name]
