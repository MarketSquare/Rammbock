#!/usr/bin/env python
from distutils.core import setup
from os.path import join, dirname

execfile(join(dirname(__file__), 'src', 'Rammbock', 'version.py'))

setup(name         = 'robotframework-rammbock',
      version      = VERSION,
      description  = 'Protocol testing library for Robot Framework',
      author       = 'Robot Framework Developers',
      author_email = 'robotframework-users@googlegroups.com',
      url          = 'http://github.com/robotframework/Rammbock/',
      package_dir  = {'' : 'src'},
      packages     = ['Rammbock', 'Rammbock.templates']
      )
