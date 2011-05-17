#!/bin/bash
pybot -c regression -L debug --variablefile  linux_vars.py --pythonpath src/ $@ atests
