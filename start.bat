@echo off
cd /d "%~dp0"
echo Starting Alpine Ascents...
start "" http://localhost:8080
node server.js
pause
