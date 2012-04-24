#!/usr/bin/env python
from robot.libdoc import libdoc
from os.path import join, dirname

libdoc(join(dirname(__file__),'src','Rammbock'), join(dirname(__file__),'doc','Rammbock.html'))