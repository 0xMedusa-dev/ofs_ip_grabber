@echo off
echo Installing IP Grabber tool...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python not found. Installing Python...
    curl -o python-installer.exe https://www.python.org/ftp/python/3.11.4/python-3.11.4-amd64.exe
    start /wait python-installer.exe /quiet InstallAllUsers=1 PrependPath=1
    del python-installer.exe
) else (
    echo Python is already installed.
)

echo Installing required libraries...
pip install -r requirements.txt

echo Creating run script...
echo @echo off > run.bat
echo python src/main.py >> run.bat
echo pause >> run.bat

echo Installation complete!
echo To run the IP Grabber tool, double-click 'run.bat' or execute:
echo   run.bat