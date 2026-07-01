@echo off
cd /d %~dp0
py -m pip install -r requirements_pcp.txt
py servidor_pcp.py
pause
