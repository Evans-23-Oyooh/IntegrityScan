#!/bin/bash
# Quick deployment fix script for PythonAnywhere
# Run this in PythonAnywhere console to fix all issues

echo "=== IntegrityScan PythonAnywhere Deployment Fix ==="
echo ""

# Navigate to project directory
cd /home/evansoyoo97/IntegrityScan
echo "✓ Changed to project directory"

# Activate virtual environment
source /home/evansoyoo97/.virtualenvs/integrityscan/bin/activate
echo "✓ Activated virtual environment"

# Update pip
echo ""
echo "Updating pip..."
pip install --upgrade pip
echo "✓ Pip updated"

# Install requirements
echo ""
echo "Installing requirements..."
pip install --upgrade -r requirements.txt --no-cache-dir
echo "✓ Requirements installed"

# Download NLTK data
echo ""
echo "Downloading NLTK data..."
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
echo "✓ NLTK data downloaded"

# Run migrations
echo ""
echo "Running database migrations..."
python manage.py migrate
echo "✓ Migrations completed"

# Collect static files
echo ""
echo "Collecting static files..."
python manage.py collectstatic --noinput
echo "✓ Static files collected"

# Verify installation
echo ""
echo "Verifying installation..."
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

echo ""
echo "=== Deployment Fix Complete ==="
echo ""
echo "Next steps:"
echo "1. Go to PythonAnywhere Web tab"
echo "2. Click 'Reload' button"
echo "3. Visit https://evansoyoo97.pythonanywhere.com"
echo ""
echo "If you see errors, check the error log in PythonAnywhere Web tab"
