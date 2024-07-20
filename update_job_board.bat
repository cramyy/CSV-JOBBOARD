@echo off
echo Installing required packages...
pip install -r requirements.txt
echo.
echo Running job board update script...
python gui.py
pause