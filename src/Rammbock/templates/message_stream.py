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
from Rammbock import logger

from Rammbock.binary_tools import to_bin


class MessageStream(object):

    def __init__(self, stream, protocol):
        self._cache = []
        self._stream = stream
        self._protocol = protocol
        self._handlers = []

    def set_handler(self, msg_template, handler_func):
        self._handlers.append((msg_template, handler_func))

    def get(self, message_template, timeout=None, header_filter=None):
        header_fields = message_template.header_parameters
        logger.trace("Get message with params %s" % header_fields)
        msg = self._get_from_cache(message_template, header_fields, header_filter)
        if msg:
            logger.trace("Cache hit. Cache currently has %s messages" % len(self._cache))
            return msg
        while True:
            header, pdu_bytes = self._protocol.read(self._stream, timeout=timeout)
            if self._matches(header, header_fields, header_filter):
                return self._to_msg(message_template, header, pdu_bytes)
            else:
                self._match_or_cache(header, pdu_bytes, header_filter)

    def _match_or_cache(self, header, pdu_bytes, header_filter):
        for template, func in self._handlers:
            if self._matches(header, template.header_parameters, header_filter):
                msg_to_be_sent = self._to_msg(template, header, pdu_bytes)
                self._get_call_handler(func)(self, msg_to_be_sent)
                return  #FIXME Make test that handled messages dont go to cache
        self._cache.append((header, pdu_bytes))

    def _get_call_handler(self,handler_name):
        module, function = handler_name.split('.')
        mod = __import__(module)
        return getattr(mod, function)

    def _get_from_cache(self, template, fields, header_filter):
        for index in range(len(self._cache)):
            header, pdu = self._cache[index]
            if self._matches(header, fields, header_filter):
                self._cache.pop(index)
                return self._to_msg(template, header, pdu)
        return None

    def _to_msg(self, template, header, pdu_bytes):
        if template.only_header:
            return header
        msg = template.decode(pdu_bytes, parent=header)
        msg._add_header(header)
        return msg

    def _matches(self, header, fields, header_filter):
        # FIXME: Matching should not be assuming matching string presentation
        if header_filter:
            if header_filter not in fields:
                raise AssertionError('Trying to filter messages by header field %s, but no value has been set for %s' %
                                     (header_filter, header_filter))
            if header[header_filter].bytes != to_bin(fields[header_filter]):
                return False
        return True

    def empty(self):
        self._cache = []
        self._stream.empty()

    def get_messages_count_in_cache(self):
        self._fill_cache()
        for msg in self._cache:
            logger.info(msg)
        return len(self._cache)

    def _fill_cache(self):
        try:
            while True:
                header, pdu_bytes = self._protocol.read(self._stream, timeout=0.2)
                self._cache.append((header, pdu_bytes))
        except:
            pass
