#!/bin/bash
export PATH=$PATH:/usr/local/bin
nosetests --with-xunit --where utest
