@ECHO OFF
set BASE=%~dp0
set DEFAULT_TARGET=
IF [%1]==[] set DEFAULT_TARGET="%BASE%atests"
pybot -c regression -L DEBUG --variablefile "%BASE%/config/win_vars.py" -d "%BASE%/reports/" --pythonpath "%BASE%src" %DEFAULT_TARGET% %*
pause
