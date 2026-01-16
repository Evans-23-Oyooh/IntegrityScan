# PythonAnywhere Deployment Checklist

## Pre-Deployment (Local Testing)

- [ ] Pull latest code changes
- [ ] Verify `requirements.txt` has all dependencies
- [ ] Test locally: `python manage.py runserver`
- [ ] Run migrations locally: `python manage.py migrate`
- [ ] Test plagiarism detection feature
- [ ] Test user registration
- [ ] Verify no errors in console

## PythonAnywhere Deployment

### Step 1: Update Code
- [ ] SSH into PythonAnywhere console
- [ ] Navigate to project: `cd /home/evansoyoo97/IntegrityScan`
- [ ] Pull latest changes: `git pull` (if using git)
- [ ] Or upload new files via web interface

### Step 2: Install Dependencies
- [ ] Activate virtual environment: `source /home/evansoyoo97/.virtualenvs/integrityscan/bin/activate`
- [ ] Upgrade pip: `pip install --upgrade pip`
- [ ] Install requirements: `pip install --upgrade -r requirements.txt --no-cache-dir`
- [ ] Verify no errors during installation

### Step 3: Download NLTK Data
- [ ] Run: `python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('punkt_tab')"`
- [ ] Verify all downloads complete successfully

### Step 4: Database Setup
- [ ] Run migrations: `python manage.py migrate`
- [ ] Verify all migrations apply successfully
- [ ] Check for any migration errors in output

### Step 5: Static Files
- [ ] Collect static files: `python manage.py collectstatic --noinput`
- [ ] Verify no errors during collection

### Step 6: Web App Reload
- [ ] Go to PythonAnywhere Web tab
- [ ] Click "Reload" button
- [ ] Wait for reload to complete (usually 10-30 seconds)

## Post-Deployment Testing

### Immediate Tests (First 5 minutes)
- [ ] Visit homepage: https://evansoyoo97.pythonanywhere.com
- [ ] Check for any error messages
- [ ] Verify page loads without 500 errors
- [ ] Check PythonAnywhere error log (should be empty or minimal)

### Functional Tests (Next 15 minutes)
- [ ] Test admin panel: https://evansoyoo97.pythonanywhere.com/admin/
- [ ] Login with superuser credentials
- [ ] Test user registration page
- [ ] Create a test user account
- [ ] Login with test account
- [ ] Submit text for plagiarism check
- [ ] Verify results display correctly
- [ ] Test other features (AI detection, etc.)

### Error Log Review
- [ ] Check PythonAnywhere error log for any errors
- [ ] Look for "ModuleNotFoundError" messages
- [ ] Look for "OperationalError" database messages
- [ ] Look for "DisallowedHost" messages
- [ ] Verify no 500 errors in recent requests

## Rollback Plan (If Issues Occur)

If deployment fails:

1. [ ] Check error log for specific error message
2. [ ] Refer to PYTHONANYWHERE_DEPLOYMENT.md troubleshooting section
3. [ ] Try individual fix steps:
   - [ ] Reinstall requirements: `pip install -r requirements.txt --force-reinstall`
   - [ ] Rerun migrations: `python manage.py migrate --run-syncdb`
   - [ ] Recollect static files: `python manage.py collectstatic --noinput`
4. [ ] Reload web app again
5. [ ] If still failing, restore previous version and investigate

## Performance Monitoring (First 24 Hours)

- [ ] Monitor error log for new errors
- [ ] Check response times (should be < 2 seconds)
- [ ] Monitor CPU usage in PythonAnywhere dashboard
- [ ] Monitor memory usage
- [ ] Check for any 500 errors in logs
- [ ] Verify all features working correctly

## Documentation

- [ ] Update deployment notes with any issues encountered
- [ ] Document any custom configurations made
- [ ] Note any performance issues or optimizations needed
- [ ] Update team on deployment status

## Sign-Off

- [ ] Deployment completed successfully
- [ ] All tests passed
- [ ] No critical errors in logs
- [ ] Application is live and functional
- [ ] Ready for production use

---

## Quick Reference Commands

```bash
# Activate virtual environment
source /home/evansoyoo97/.virtualenvs/integrityscan/bin/activate

# Install requirements
pip install --upgrade -r requirements.txt --no-cache-dir

# Download NLTK data
python -c "import nltk; nltk.download('punkt'); nltk.download('wordnet'); nltk.download('punkt_tab')"

# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic --noinput

# Check Django version
python -c "import django; print(django.VERSION)"

# Check if transformers installed
python -c "import transformers; print('Transformers OK')"

# Check if nltk installed
python -c "import nltk; print('NLTK OK')"

# View error log
tail -f /var/log/evansoyoo97_pythonanywhere_com_wsgi.log
```

---

## Contact & Support

If you encounter issues:

1. Check PYTHONANYWHERE_DEPLOYMENT.md
2. Review PythonAnywhere error logs
3. Check Django documentation
4. Review application logs

---

**Deployment Date:** _______________
**Deployed By:** _______________
**Status:** ☐ Successful ☐ Failed ☐ Partial
**Notes:** _______________________________________________

