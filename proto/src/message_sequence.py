from OrderedDict import OrderedDict

def ip_name(ip, port):
    return '%s:%s' % (ip,port)

class MessageSequence(object):

    def __init__(self):
        self.operators = OrderedDict()
        self.sequence = []

    def _operator(self, name, ip, port):
        ip_port = ip_name(ip,port)
        if ip_port not in self.operators:
            self.operators[ip_port] = Operator(ip_port, name)
        else:
            self.operators[ip_port].name = name
        return self.operators[ip_port]

    def _get_operator(self, ip_port):
        if ip_port not in self.operators:
            self.operators[ip_port] = Operator(ip_port)
        return self.operators[ip_port]

    def send(self, sender_name, sender, receiver, protocol, message_name, error=''):
        self.sequence.append((self._operator(sender_name, *sender),self._get_operator(ip_name(*receiver)),
                              '%s:%s' % (protocol, message_name), error, 'sent'))

    def receive(self, receiver_name, receiver, sender, protocol, message_name, error=''):
        row = (self._get_operator(ip_name(*sender)), self._operator(receiver_name, *receiver),
                                    '%s:%s' % (protocol, message_name), error, 'received')
        for i in reversed(range(len(self.sequence))):
            if self._matches(self.sequence[i], receiver, sender):
                self.sequence[i] = row
                return
        self.sequence.append(row)

    def _matches(self, msg, receiver, sender):
        return msg[0].ip_name == ip_name(*sender) and \
               msg[1].ip_name == ip_name(*receiver) and \
               msg[-1] == 'sent'

    def get_operators(self):
        return (operator.name for operator in self.operators.values())

    def get(self):
        return ((str(elem) for elem in row) for row in self.sequence)


class Operator(object):

    def __init__(self, ip_name, name=None):
        self.ip_name = ip_name
        self.name = name if name else ip_name

    def __str__(self):
        return self.name