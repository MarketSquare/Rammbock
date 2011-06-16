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
        try:
            headers = __import__("rammbock.protocols."+self.protocol+"."+self.version, fromlist= ['kekkonen'])
        except ImportError:
            raise Exception (ImportError, "Unknown apllication protocol: '%s' or version: '%s'" % (self.protocol, self.version))
        try:
            self.header = headers.message_headers[self.message_name]
        except KeyError:
            raise Exception (KeyError, "Unknown message type: '%s'" % self.message_name)