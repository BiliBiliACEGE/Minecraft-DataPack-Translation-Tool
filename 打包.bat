@echo off
pyinstaller main.py  --noconsole --icon=icon.ico --add-data "langs;langs"
echo ===== ������ =====
dir dist\main.exe
pause