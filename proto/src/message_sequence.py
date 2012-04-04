from OrderedDict import OrderedDict

def ip_name(ip, port):
    return '%s:%s' % (ip,port)

def msg_name(protocol, message_name):
    if protocol and message_name:
        return '%s:%s' % (protocol, message_name)
    return message_name or 'binary'

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
                              msg_name(protocol, message_name), error, 'sent'))

    def receive(self, receiver_name, receiver, sender, protocol, message_name, error=''):
        sender_ip_name = ip_name(*sender)
        row = (self._get_operator(sender_ip_name), self._operator(receiver_name, *receiver),
                                  msg_name(protocol, message_name), error, 'received')
        if self.is_named_operator(sender_ip_name):
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

    def is_named_operator(self, ip_name):
        return ip_name in self.operators and ip_name != self.operators[ip_name].name


class Operator(object):

    def __init__(self, ip_name, name=None):
        self.ip_name = ip_name
        self.name = name or ip_name

    def __str__(self):
        return self.name


class SeqdiagGenerator(object):

    template = """diagram {
%s}
"""

    def generate(self, operators, sequence):
        result = ''
        operators = list(operators)
        for row in sequence:
            if operators.index(row[0]) < operators.index(row[1]):
                result +='    %s -> %s [label = "%s"];\n' % (row[0],row[1], row[2])
            else:
                result +='    %s <- %s [label = "%s"];\n' % (row[1],row[0], row[2])
        return self.template % result