# 🚀 Quick Setup Instructions

## Step 1: Install Python
Since Python is not detected on your system, please install it first:

### Windows:
1. Go to https://python.org/downloads/
2. Download Python 3.8 or newer
3. Run the installer and **CHECK "Add Python to PATH"**
4. Restart your command prompt

### Alternative (Microsoft Store):
1. Open Microsoft Store
2. Search for "Python 3.11" or "Python 3.10"
3. Install it

## Step 2: Run the Simple Version
Once Python is installed, you can run the basic version immediately:

```bash
python simple_detector.py
```

This version works with just built-in Python libraries and includes:
- ✅ Plagiarism detection using multiple algorithms
- ✅ Document database storage
- ✅ Basic text correction
- ✅ Interactive command-line interface

## Step 3: Upgrade to Full Version (Optional)
For the advanced AI-powered version with web interface:

```bash
pip install flask nltk scikit-learn sentence-transformers transformers torch requests beautifulsoup4
python app.py
```

Then visit: http://localhost:5000

## 🎯 Quick Test
After installing Python, try this:

1. Run: `python simple_detector.py`
2. Choose option 1 (Check text for plagiarism)
3. Enter: "Machine learning enables computers to learn without programming"
4. See the plagiarism detection in action!

## 📁 Files Overview
- `simple_detector.py` - Basic version (no dependencies)
- `app.py` - Full web version (requires packages)
- `plagiarism_detector.py` - Advanced detection engine
- `plagiarism_corrector.py` - AI-powered correction
- `cli.py` - Command-line interface

## 🔧 Troubleshooting
- If "python" doesn't work, try "py" or "python3"
- Make sure Python is added to your system PATH
- Restart command prompt after Python installation