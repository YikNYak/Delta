@echo off
chcp 65001 >nul
set PYTHONIOENCODING=utf-8
set PYTHONUTF8=1
python -X utf8 "%~dp0Delta.py" %*
if errorlevel 1 py -3 -X utf8 "%~dp0Delta.py" %*
