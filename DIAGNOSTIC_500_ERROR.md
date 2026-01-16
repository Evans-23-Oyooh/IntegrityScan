# PythonAnywhere 500 Error Diagnostic

## Steps to Find the Error

### 1. Check Error Log on PythonAnywhere
- Go to: https://www.pythonanywhere.com/user/evansoyoo97/
- Click: **Web** tab
- Scroll down to: **Error log**
- Look for the most recent error message

### 2. Common 500 Error Causes

**Missing Template:**
```
TemplateDoesNotExist: auth/login.html
```
→ Check if template exists in `/templates/auth/`

**Import Error:**
```
ModuleNotFoundError: No module named 'X'
```
→ Run: `pip install -r requirements.txt`

**Database Error:**
```
OperationalError: no such table
```
→ Run: `python manage.py migrate`

**Syntax Error:**
```
SyntaxError: invalid syntax
```
→ Check Python file syntax

### 3. Quick Fixes to Try

**Option 1: Pull latest code**
```bash
cd /home/evansoyoo97/IntegrityScan
git pull origin main
```

**Option 2: Reload web app**
- PythonAnywhere Web tab → Click "Reload"

**Option 3: Run Django check**
```bash
python manage.py check
```

**Option 4: Restart Python**
- PythonAnywhere Web tab → Click "Reload"

### 4. Enable Debug Mode (Temporary)

Edit `textanalyzer/settings.py`:
```python
DEBUG = True  # Temporarily enable for error details
```

Then reload web app to see detailed error.

### 5. Check Specific Files

Verify these files exist:
- [ ] `/templates/auth/login.html`
- [ ] `/templates/index.html`
- [ ] `/templates/base.html`
- [ ] `/analyzer/urls.py` (no duplicate imports)
- [ ] `/analyzer/auth_views.py` (all functions defined)

### 6. Common Issues in This Project

**Issue 1: Missing login.html template**
→ Check: `/templates/auth/login.html` exists

**Issue 2: Transformers import error**
→ Check: `pip list | grep transformers`

**Issue 3: NLTK data missing**
→ Run: `python -c "import nltk; nltk.download('punkt')"`

**Issue 4: Database not migrated**
→ Run: `python manage.py migrate`

## Next Steps

1. Check PythonAnywhere error log
2. Identify the specific error message
3. Apply the corresponding fix above
4. Reload web app
5. Test again

---

**Need help?** Share the error message from PythonAnywhere error log.
