@ECHO OFF
set BASE=%~dp0
set DEFAULT_TARGET=
IF [%1]==[] set DEFAULT_TARGET="%BASE%atest"
pybot -c regression -L DEBUG --pythonpath "%BASE%src" %DEFAULT_TARGET% %*
pause
