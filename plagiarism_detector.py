import re
import hashlib
import sqlite3
from difflib import SequenceMatcher
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import requests
from bs4 import BeautifulSoup

class PlagiarismDetector:
    def __init__(self):
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.vectorizer = TfidfVectorizer(stop_words='english', ngram_range=(1, 3))
        self.init_database()
        self._download_nltk_data()
        
    def _download_nltk_data(self):
        try:
            nltk.data.find('tokenizers/punkt')
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('punkt')
            nltk.download('stopwords')
    
    def init_database(self):
        self.conn = sqlite3.connect('plagiarism_db.sqlite', check_same_thread=False)
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS documents (
                id INTEGER PRIMARY KEY,
                title TEXT,
                content TEXT,
                fingerprint TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        self.conn.commit()
    
    def preprocess_text(self, text):
        text = re.sub(r'[^\w\s]', '', text.lower())
        tokens = word_tokenize(text)
        stop_words = set(stopwords.words('english'))
        return ' '.join([word for word in tokens if word not in stop_words])
    
    def generate_fingerprint(self, text):
        return hashlib.md5(self.preprocess_text(text).encode()).hexdigest()
    
    def n_gram_similarity(self, text1, text2, n=3):
        def get_ngrams(text, n):
            words = text.split()
            return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
        
        ngrams1 = set(get_ngrams(self.preprocess_text(text1), n))
        ngrams2 = set(get_ngrams(self.preprocess_text(text2), n))
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1.intersection(ngrams2))
        union = len(ngrams1.union(ngrams2))
        return intersection / union if union > 0 else 0.0
    
    def semantic_similarity(self, text1, text2):
        embeddings = self.model.encode([text1, text2])
        return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
    
    def tfidf_similarity(self, text1, text2):
        try:
            tfidf_matrix = self.vectorizer.fit_transform([text1, text2])
            return cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        except:
            return 0.0
    
    def sequence_similarity(self, text1, text2):
        return SequenceMatcher(None, text1, text2).ratio()
    
    def detect_plagiarism(self, text, threshold=0.7):
        results = []
        
        # Check against database
        cursor = self.conn.execute("SELECT title, content FROM documents")
        for title, content in cursor.fetchall():
            similarities = {
                'ngram': self.n_gram_similarity(text, content),
                'semantic': self.semantic_similarity(text, content),
                'tfidf': self.tfidf_similarity(text, content),
                'sequence': self.sequence_similarity(text, content)
            }
            
            # Weighted average
            overall_similarity = (
                similarities['semantic'] * 0.4 +
                similarities['ngram'] * 0.3 +
                similarities['tfidf'] * 0.2 +
                similarities['sequence'] * 0.1
            )
            
            if overall_similarity > threshold:
                results.append({
                    'source': title,
                    'similarity': overall_similarity,
                    'details': similarities,
                    'plagiarized_content': content[:200] + "..."
                })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    def web_search_check(self, text, num_results=5):
        """Check against web sources"""
        try:
            query = ' '.join(text.split()[:10])  # First 10 words
            url = f"https://www.google.com/search?q={query}"
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            
            response = requests.get(url, headers=headers, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            results = []
            for result in soup.find_all('div', class_='g')[:num_results]:
                link_elem = result.find('a')
                if link_elem and link_elem.get('href'):
                    try:
                        page_response = requests.get(link_elem['href'], headers=headers, timeout=5)
                        page_soup = BeautifulSoup(page_response.content, 'html.parser')
                        page_text = page_soup.get_text()[:1000]
                        
                        similarity = self.semantic_similarity(text, page_text)
                        if similarity > 0.6:
                            results.append({
                                'url': link_elem['href'],
                                'similarity': similarity,
                                'snippet': page_text[:200] + "..."
                            })
                    except:
                        continue
            
            return results
        except:
            return []
    
    def add_document(self, title, content):
        fingerprint = self.generate_fingerprint(content)
        self.conn.execute(
            "INSERT INTO documents (title, content, fingerprint) VALUES (?, ?, ?)",
            (title, content, fingerprint)
        )
        self.conn.commit()
    
    def comprehensive_check(self, text):
        """Perform comprehensive plagiarism check"""
        return {
            'database_results': self.detect_plagiarism(text),
            'web_results': self.web_search_check(text),
            'fingerprint': self.generate_fingerprint(text)
        }