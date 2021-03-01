Rammbock
========

.. contents::
   :local:
   
**Note:** This project is currently without a maintainer and is not being updated. If you are interested in taking over maintaining this project, please contact chair@robotframework.org

Introduction
------------

Generic network protocol test library for Robot Framework, which offers an easy way to specify network packets and inspect the results of sent / received packets. Library offers Domain Specific Language for packet specification.

Downloads are available at https://pypi.python.org/pypi/robotframework-rammbock

Installation instructions
-------------------------

Precondiditons
~~~~~~~~~~~~~~
You need to have Robot Framework installed as a precondition.

Installation
~~~~~~~~~~~~

-  With PIP Installer::

      pip install robotframework-rammbock

- With Setup.py Download and extract .zip or .tar.gz. Execute command in extracted folder::

      python setup.py install

Examples
--------

We have examples from following protocols:

- GTPv2
- Diameter
- DNS

Examples can be found from our acceptance test cases:
https://github.com/robotframework/Rammbock/tree/master/atest

Documentation
-------------
- See the userguide at https://github.com/robotframework/Rammbock/wiki/RammbockUserGuide
- See keyword documentation at https://robotframework.github.com/Rammbock/index.html
