from xml.etree import ElementTree as ET
import sys
import re

source = sys.argv[1]
kw_stack = []

SENDS = re.compile('.*Rammbock\..*Sends Message')
RECEIVES = re.compile('.*Rammbock\..*Receives Message')

def _get_message_text(messages):
    for msg in messages:
        if msg.text.startswith('Received Message') or msg.text.startswith('Message'):
            return msg.text
    return "Message content not found, run at DEBUG level to generate message contents"  

def _print_element(elem, separator):
    print('\n'.join(kw_stack))
    print(separator)
    print(_get_message_text(elem.findall('msg')))
    print('--------------------------------------')

for event, elem in ET.iterparse(source, events=('start', 'end')):
    if elem.tag not in ("kw", "test", "suite", "statistics"):
        continue
    elif elem.tag == "statistics":
        break
    elif event == 'start':
        name = elem.get('name')
        kw_stack.append(name)
        if SENDS.search(name):
            _print_element(elem, '---->>>')
        elif RECEIVES.search(name):
            _print_element(elem, '<<<----')        
    elif event == 'end':
        kw_stack.pop()
