@echo off
REM Complete setup script for IntegrityScan

echo ========================================
echo IntegrityScan - Complete Setup
echo ========================================
echo.

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    echo Virtual environment created
    echo.
)

REM Activate virtual environment
call venv\Scripts\activate.bat
echo Virtual environment activated
echo.

REM Install requirements
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo Error installing requirements
    pause
    exit /b 1
)
echo Dependencies installed successfully
echo.

REM Download NLTK data
echo Downloading NLTK data...
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
echo NLTK data downloaded
echo.

REM Run migrations
echo Running database migrations...
python manage.py migrate
if %errorlevel% neq 0 (
    echo Error running migrations
    pause
    exit /b 1
)
echo Migrations completed
echo.

REM Collect static files
echo Collecting static files...
python manage.py collectstatic --noinput
if %errorlevel% neq 0 (
    echo Error collecting static files
    pause
    exit /b 1
)
echo Static files collected
echo.

REM Verify installation
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

echo ========================================
echo Setup Complete!
echo ========================================
echo.
echo Next steps:
echo 1. Run: python manage.py runserver
echo 2. Visit: http://localhost:8000
echo 3. Test the application
echo.
pause
