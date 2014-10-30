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

import threading
import time

from robot.api import logger


MESSAGE_QUEUE = {}
THREAD_NAMES = {}
LOCK = threading.RLock()


def trace(msg, html=False):
    _log('trace', msg, html)


def debug(msg, html=False):
    _log('debug', msg, html)


def info(msg, html=False):
    _log('info', msg, html)


def warn(msg, html=False):
    _log('warn', msg, html)


def _log(level, msg, html):
    with LOCK:
        thread = threading.currentThread()
        if thread.getName() == 'MainThread':
            getattr(logger, level)(msg, html=html)
        else:
            MESSAGE_QUEUE.setdefault(thread.ident, []).append((round(time.time() * 1000),
                                                               level, msg, html))
            THREAD_NAMES[thread.ident] = thread.getName()


def reset_background_messages():
    with LOCK:
        MESSAGE_QUEUE.clear()


def log_background_messages():
    with LOCK:
        for thread in MESSAGE_QUEUE:
            print "*HTML* <b>Messages from thread: %s (%s)</b>" % (THREAD_NAMES[thread], thread)
            for timestamp, level, msg, html in MESSAGE_QUEUE[thread]:
                print "*%s:%d* %s" % (level.upper(), timestamp, msg)
