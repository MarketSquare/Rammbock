#  Copyright 2014 Nokia Siemens Networks Oyj
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
from __future__ import with_statement
import subprocess
from .ordered_dict import OrderedDict
from .logger import logger


def ip_name(ip, port):
    return '%s:%s' % (ip, port)


def msg_name(protocol, message_name):
    if protocol and message_name:
        return '%s:%s' % (protocol, message_name)
    return message_name or 'binary'


class MessageSequence(object):

    def __init__(self):
        self.operators = OrderedDict()
        self.sequence = []

    def _operator(self, name, ip, port):
        ip_port = ip_name(ip, port)
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
        self.sequence.append((self._operator(sender_name, *sender),
                              self._get_operator(ip_name(*receiver)),
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
        sequence = list(sequence)
        for row in sequence[-15:]:
            row = list(row)
            if operators.index(row[0]) < operators.index(row[1]):
                result += '    "%s" -> "%s" %s;\n' % (row[0], row[1], self._get_label(row))
            else:
                result += '    "%s" <- "%s" %s;\n' % (row[1], row[0], self._get_label(row))
        return self.template % result

    def _get_label(self, row):
        if row[3]:
            return '[label = "%s - %s", color = red]' % (row[2], row[3])
        else:
            return '[label = "%s"]' % row[2]

    def compile(self, path, sequence):
        diagram = self.generate(sequence.get_operators(), sequence.get())
        with open(path, 'w') as output:
            output.write(diagram)
        rc = 1
        try:
            rc = subprocess.call(["seqdiag", '-o', path + '.png', path])
        except:
            pass
        self._print_link(path, rc)

    def _print_link(self, path, rc):
        if rc == 0:
            name = path + '.png'
            logger.info('<a href="%s"><img src="%s"></a>' % (name, name), True)
        else:
            logger.debug('Message sequence generation with seqdiag failed. Linking sequence file instead.')
            logger.info('<a href="%s">Message sequence</a>' % path, True)
