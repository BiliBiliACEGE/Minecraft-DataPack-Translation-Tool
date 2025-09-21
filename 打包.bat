@echo off
pyinstaller main.py  --noconsole --icon=icon.ico --add-data "langs;langs"
echo ===== 打包完成 =====
dir dist\main.exe
pause