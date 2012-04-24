#!/usr/bin/env python
from robot.libdoc import libdoc
from os.path import join, dirname

execfile(join(dirname(__file__), 'src', 'Rammbock', 'version.py'))

libdoc(join(dirname(__file__),'src','Rammbock'), join(dirname(__file__),'Rammbock-%s.html' % VERSION))