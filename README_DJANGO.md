# 🚀 Django Text Analyzer System

A comprehensive Django web application for text analysis, plagiarism detection, AI content detection, URL shortening, and QR code generation.

## ✨ Features

### 📝 Text Analysis
- **Plagiarism Detection**: Multi-algorithm detection using N-gram analysis, semantic similarity, and document fingerprinting
- **AI Content Detection**: Identify AI-generated text and provide humanization suggestions
- **Document Management**: Store and manage reference documents for comparison

### 🔗 URL Management
- **URL Shortener**: Create short, trackable links with click analytics
- **Custom Short Codes**: Generate secure, random short codes
- **Click Tracking**: Monitor URL performance and usage statistics

### 📱 QR Code Generation
- **Multiple Types**: URL, Text, vCard (contacts), WiFi credentials
- **High Quality**: PNG format with customizable size and error correction
- **Batch Generation**: Create multiple QR codes efficiently

### 🌐 Web Interface & API
- **Modern UI**: Bootstrap-based responsive design
- **REST API**: JSON endpoints for all features
- **Admin Panel**: Django admin for data management
- **Analytics Dashboard**: Usage statistics and insights

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager

### Quick Start

1. **Install Python** (if not already installed):
   - Windows: Download from https://python.org/downloads/
   - Make sure to check "Add Python to PATH"

2. **Install Dependencies**:
   ```bash
   pip install -r requirements_django.txt
   ```

3. **Setup Database**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. **Create Admin User** (optional):
   ```bash
   python manage.py createsuperuser
   ```

5. **Run the Server**:
   ```bash
   python manage.py runserver
   ```

6. **Access the Application**:
   - Web Interface: http://localhost:8000
   - Admin Panel: http://localhost:8000/admin

## 📊 Usage

### Web Interface
Navigate to different sections using the sidebar:
- **Dashboard**: Overview and quick actions
- **Plagiarism Check**: Analyze text for plagiarism
- **AI Detection**: Detect and humanize AI content
- **URL Shortener**: Create short links
- **QR Generator**: Generate QR codes
- **Documents**: Manage reference documents
- **Analytics**: View usage statistics

### API Endpoints

#### Plagiarism Check
```bash
POST /api/plagiarism-check/
Content-Type: application/json

{
    "text": "Your text to check",
    "threshold": 0.7
}
```

#### AI Detection
```bash
POST /api/ai-detection/
Content-Type: application/json

{
    "text": "Text to analyze for AI content"
}
```

#### URL Shortener
```bash
POST /api/shorten-url/
Content-Type: application/json

{
    "url": "https://example.com/very-long-url"
}
```

#### QR Code Generation
```bash
POST /api/generate-qr/
Content-Type: application/json

{
    "qr_type": "url",
    "content": "https://example.com"
}
```

## 🔧 Configuration

### Settings
Edit `textanalyzer/settings.py` for:
- Database configuration
- Static files settings
- Security settings
- API permissions

### Environment Variables
Create a `.env` file for sensitive settings:
```
SECRET_KEY=your-secret-key-here
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
```

## 📈 Advanced Features

### Plagiarism Detection Algorithms
1. **N-gram Analysis**: Compares word sequences
2. **Semantic Similarity**: Meaning-based comparison
3. **Document Fingerprinting**: Unique content signatures
4. **Sequence Matching**: Character-level similarity

### AI Detection Methods
1. **Pattern Recognition**: Identifies AI writing patterns
2. **Heuristic Analysis**: Common AI indicators
3. **Text Humanization**: Makes content more natural
4. **Confidence Scoring**: Probability assessment

### URL Shortener Features
1. **Random Code Generation**: Secure short codes
2. **Click Tracking**: Detailed analytics
3. **URL Validation**: Security checks
4. **Bulk Operations**: Batch processing

### QR Code Capabilities
1. **Multiple Formats**: URL, Text, vCard, WiFi
2. **Error Correction**: Robust scanning
3. **Custom Sizing**: Adjustable dimensions
4. **High Quality**: PNG output

## 🔒 Security Features

- CSRF protection
- SQL injection prevention
- Input validation and sanitization
- Secure file handling
- Admin authentication

## 📱 Mobile Responsive

The interface is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile phones
- All modern browsers

## 🚀 Deployment

### Local Development
```bash
python manage.py runserver 0.0.0.0:8000
```

### Production Deployment
1. Set `DEBUG = False` in settings
2. Configure proper database (PostgreSQL recommended)
3. Set up static file serving
4. Use WSGI server (Gunicorn)
5. Configure reverse proxy (Nginx)

## 🤝 API Integration Examples

### Python
```python
import requests

# Plagiarism check
response = requests.post('http://localhost:8000/api/plagiarism-check/', 
    json={'text': 'Your text', 'threshold': 0.7})
result = response.json()

# AI detection
response = requests.post('http://localhost:8000/api/ai-detection/', 
    json={'text': 'Your text'})
result = response.json()
```

### JavaScript
```javascript
// URL shortening
fetch('/api/shorten-url/', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({url: 'https://example.com'})
})
.then(response => response.json())
.then(data => console.log(data));
```

## 📊 Database Schema

- **Documents**: Reference documents for plagiarism checking
- **PlagiarismCheck**: Plagiarism analysis results
- **AIDetection**: AI content detection results
- **URLShortener**: Short URL mappings and analytics
- **QRCode**: Generated QR codes and metadata

## 🔍 Troubleshooting

### Common Issues
1. **Module not found**: Install requirements with `pip install -r requirements_django.txt`
2. **Database errors**: Run migrations with `python manage.py migrate`
3. **Static files**: Collect static files with `python manage.py collectstatic`
4. **Port conflicts**: Change port with `python manage.py runserver 8080`

## 📝 License

Open source project. Feel free to modify and distribute.

## 🚀 Future Enhancements

- [ ] Multi-language support
- [ ] Advanced ML models
- [ ] Real-time collaboration
- [ ] Cloud storage integration
- [ ] Advanced analytics
- [ ] Mobile app
- [ ] API rate limiting
- [ ] Webhook support