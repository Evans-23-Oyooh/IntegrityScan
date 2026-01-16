# PythonAnywhere Deployment Guide

## Issues Fixed

This guide addresses the following errors from your PythonAnywhere logs:

1. ✅ `ModuleNotFoundError: No module named 'allauth'` - Removed from INSTALLED_APPS
2. ✅ `ModuleNotFoundError: No module named 'transformers'` - Added to requirements.txt
3. ✅ `ModuleNotFoundError: No module named 'nltk'` - Already in requirements.txt
4. ✅ `Invalid HTTP_HOST header` - Fixed ALLOWED_HOSTS configuration
5. ✅ `no such table: analyzer_urlshortener` - Database migrations needed

## Step-by-Step Deployment Instructions

### 1. Update Dependencies

On PythonAnywhere console, run:

```bash
cd /home/evansoyoo97/IntegrityScan
source /home/evansoyoo97/.virtualenvs/integrityscan/bin/activate
pip install --upgrade -r requirements.txt
```

**Note:** If you get memory errors with `transformers` or `torch`, use:

```bash
pip install transformers==4.30.0 --no-cache-dir
pip install torch==2.0.0 --no-cache-dir
```

### 2. Download NLTK Data

```bash
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('wordnet'); nltk.download('punkt_tab')"
```

### 3. Run Database Migrations

```bash
python manage.py migrate
```

This will create all required tables:
- `analyzer_urlshortener`
- `auth_user`
- And all other Django tables

### 4. Create Superuser (First Time Only)

```bash
python manage.py createsuperuser
```

### 5. Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### 6. Reload Web App

In PythonAnywhere web app settings:
- Go to **Web** tab
- Click **Reload** button for your web app

## Configuration Checklist

### Environment Variables

Set these in PythonAnywhere **Web** tab → **WSGI configuration file**:

```python
os.environ.setdefault('DEBUG', 'False')
os.environ.setdefault('ALLOWED_HOSTS', 'evansoyoo97.pythonanywhere.com')
os.environ.setdefault('SECRET_KEY', 'your-secure-secret-key-here')
```

### ALLOWED_HOSTS

Already configured in `settings.py`:
```python
ALLOWED_HOSTS = os.environ.get('ALLOWED_HOSTS', 'localhost,127.0.0.1,evansoyoo97.pythonanywhere.com').split(',')
```

### Database

Using SQLite by default. For production, consider PostgreSQL:

```bash
pip install psycopg2-binary
```

Then update `settings.py` DATABASE configuration.

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'transformers'"

**Solution:**
```bash
pip install transformers --no-cache-dir
```

If memory-limited, use a lighter model or skip transformers features.

### Issue: "no such table: analyzer_urlshortener"

**Solution:**
```bash
python manage.py migrate
```

### Issue: "Invalid HTTP_HOST header"

**Solution:** Already fixed in `settings.py`. If still occurring:

1. Check ALLOWED_HOSTS in settings.py
2. Verify domain in PythonAnywhere web app settings
3. Reload web app

### Issue: "ModuleNotFoundError: No module named 'nltk'"

**Solution:**
```bash
pip install nltk
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"
```

### Issue: Memory Errors During Installation

**Solution:** Install packages one at a time:

```bash
pip install Django==4.2.0
pip install djangorestframework==3.14.0
pip install transformers==4.30.0 --no-cache-dir
# ... continue with other packages
```

## Performance Optimization

### For PythonAnywhere Free Tier:

1. **Disable heavy features** in `services.py`:
   - Comment out transformers imports if not needed
   - Use heuristic AI detection instead of ML models

2. **Optimize database queries**:
   - Add database indexes
   - Use `select_related()` and `prefetch_related()`

3. **Cache static files**:
   - Already configured with WhiteNoise
   - Run `collectstatic` after each deployment

### For Paid Tier:

1. Use PostgreSQL instead of SQLite
2. Enable caching with Redis
3. Use Celery for background tasks

## Deployment Checklist

- [ ] Update requirements.txt
- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Download NLTK data
- [ ] Run migrations: `python manage.py migrate`
- [ ] Create superuser: `python manage.py createsuperuser`
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Verify ALLOWED_HOSTS configuration
- [ ] Reload web app in PythonAnywhere
- [ ] Test application at https://evansoyoo97.pythonanywhere.com
- [ ] Check error logs for any remaining issues

## Testing After Deployment

1. **Test homepage:**
   ```
   https://evansoyoo97.pythonanywhere.com/
   ```

2. **Test admin panel:**
   ```
   https://evansoyoo97.pythonanywhere.com/admin/
   ```

3. **Test plagiarism detection:**
   - Register a new account
   - Submit text for plagiarism check
   - Verify results display correctly

4. **Check logs:**
   - PythonAnywhere → Web → Error log
   - Look for any remaining errors

## Quick Commands Reference

```bash
# Activate virtual environment
source /home/evansoyoo97/.virtualenvs/integrityscan/bin/activate

# Install requirements
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Run development server (local testing)
python manage.py runserver

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet')"
```

## Support

If you encounter issues:

1. Check PythonAnywhere error logs
2. Review this guide's troubleshooting section
3. Verify all steps were completed
4. Check Django documentation: https://docs.djangoproject.com/

---

**Last Updated:** 2026-01-15
**Status:** Ready for deployment
