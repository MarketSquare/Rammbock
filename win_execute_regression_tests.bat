@ECHO OFF
set BASE=%~dp0
set DEFAULT_TARGET=
IF [%1]==[] set DEFAULT_TARGET="%BASE%atests"
pybot -c regression -L DEBUG --variablefile "%BASE%win_vars.py" --pythonpath "%BASE%src" %DEFAULT_TARGET% %*
pause