@echo off
REM Quick deployment fix script for local testing
REM Run this in command prompt to verify all dependencies

echo === IntegrityScan Local Deployment Verification ===
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo Virtual environment activated

REM Update pip
echo.
echo Updating pip...
python -m pip install --upgrade pip
echo Pip updated

REM Install requirements
echo.
echo Installing requirements...
pip install --upgrade -r requirements.txt
echo Requirements installed

REM Download NLTK data
echo.
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
echo NLTK data downloaded

REM Run migrations
echo.
echo Running database migrations...
python manage.py migrate
echo Migrations completed

REM Collect static files
echo.
echo Collecting static files...
python manage.py collectstatic --noinput
echo Static files collected

REM Verify installation
echo.
echo Verifying installation...
python -c "
import django
import nltk
import transformers
import torch
print('✓ Django:', django.VERSION)
print('✓ NLTK available')
print('✓ Transformers available')
print('✓ PyTorch available')
"

echo.
echo === Deployment Verification Complete ===
echo.
echo Next steps:
echo 1. Run: python manage.py runserver
echo 2. Visit: http://localhost:8000
echo 3. Test the application
echo.
pause
