@echo off

REM Run the GUI executable
start /wait gui.exe

REM Change to the repository directory
cd /d %~dp0

REM Git operations
git add .
git commit -m "Update job listings"
git push origin main

echo Update complete. Press any key to exit.
pause >nul