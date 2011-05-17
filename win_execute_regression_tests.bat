@ECHO OFF
pybot -c regression -L debug --variablefile win_vars.py --pythonpath src\ %1 %2 atests\
