
class Message(object):

    def __init__(self, name=None):
        self._headers = []
        self._infoElements = []

        if name != None:
            #parse
            pass

    def addHeader(self, name, value, length):
        self._headers += ([name, value, length])

    def addIe(self, name, value, length):
        self._infoElements += ([name, value, length])


    
