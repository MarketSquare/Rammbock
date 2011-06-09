class Message():
    header = []
    ie = []

    def __init__(self, name):
        self.header.append(('Request Method', 'GET'))
        self.header.append(('Request URI', 'http://www.iltalehti.fi/favicon.ico'))
        self.header.append(('Request Version', "HTTP/1.1"))
        self.ie.append(('HOST', 'www.iltalehti.fi'))