@echo off
IF EXIST "venv\Scripts\activate.bat" (
    CALL "venv\Scripts\activate.bat"
)
python pydit.py %*