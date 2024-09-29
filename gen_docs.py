#!/usr/bin/env python
from robot.libdoc import libdoc
from os.path import join, dirname

exec(compile(open(join(dirname(__file__), 'src', 'Rammbock', 'version.py')).read(), 'version.py', 'exec'))

libdoc(join(dirname(__file__),'src','Rammbock'), join(dirname(__file__),'Rammbock-%s.html' % VERSION))