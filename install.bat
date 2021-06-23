ECHO OFF
pip install virtualenv
virtualenv.exe venv
call venv\Scripts\activate.bat
pip install -r requirements.txt
git update-index --assume-unchanged NAS.txt
ECHO Installation complete!
PAUSE