class HeaderSchema(object):
    headers = []

    def __init__(self, name):
        if name == 'http_get':
            self.headers = ['Request Method', 'Request URI', 'Request Version']