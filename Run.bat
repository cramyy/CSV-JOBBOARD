@echo off
:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed. Installing Python...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://www.python.org/ftp/python/3.12.4/python-3.12.4-amd64.exe' -OutFile 'python_installer.exe'}"
    python_installer.exe /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    del python_installer.exe
    
    :: Add Python to PATH
    setx PATH "%PATH%;C:\Program Files\Python312;C:\Program Files\Python312\Scripts" /M
    setx PATH "%PATH%;C:\Program Files\Python312;C:\Program Files\Python312\Scripts"
) else (
    echo Python is already installed.
)

:: Check if Git is installed
git --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Git is not installed. Installing Git...
    powershell -Command "& {Invoke-WebRequest -Uri 'https://github.com/git-for-windows/git/releases/download/v2.45.2.windows.1/Git-2.45.2-64-bit.exe' -OutFile 'git_installer.exe'}"
    git_installer.exe /VERYSILENT /NORESTART /ALLUSERS
    del git_installer.exe
    
    :: Add Git to PATH
    setx PATH "%PATH%;C:\Program Files\Git\cmd" /M
    setx PATH "%PATH%;C:\Program Files\Git\cmd"
) else (
    echo Git is already installed.
)

:: Refresh environment variables
echo Refreshing environment variables...
for /f "delims=" %%i in ('path') do (
    set "PATH=%%i"
)

:: Clone or update the repository
if exist CSV-JOBBOARD (
    echo Repository folder already exists. Updating...
    cd CSV-JOBBOARD
    git fetch --all
    git reset --hard origin/main
    cd ..
) else (
    echo Cloning the repository...
    git clone https://github.com/cramyy/CSV-JOBBOARD.git
)

cd CSV-JOBBOARD

:: Check if req.txt exists and install requirements if it does
if exist req.txt (
    echo Installing requirements from req.txt...
    pip install -r req.txt
) else (
    echo req.txt not found. Skipping requirements installation.
)

:: Run guii.py
echo Running gui.py...
python gui.py
pause