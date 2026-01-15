import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import sent_tokenize

try:
    from sentence_transformers import SentenceTransformer
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

class ModernPlagiarismDetector:
    def __init__(self):
        self._download_nltk_data()
        if TRANSFORMERS_AVAILABLE:
            try:
                self.model = SentenceTransformer('all-MiniLM-L6-v2')
            except:
                self.model = None
        else:
            self.model = None
    
    def _download_nltk_data(self):
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab', quiet=True)
    
    def detect_plagiarism(self, text, documents, threshold=0.7):
        results = []
        
        # Detect AI patterns
        ai_score = self._detect_ai_patterns(text)
        if ai_score > 0.25:
            results.append({
                'document_id': 'ai_generated',
                'title': 'AI-Generated Content Detected',
                'similarity': ai_score,
                'details': {'ai_pattern_score': ai_score}
            })
        
        # Semantic similarity check against documents
        if self.model and documents.exists():
            text_embedding = self.model.encode(text, convert_to_tensor=False)
            
            for doc in documents:
                doc_embedding = self.model.encode(doc.content, convert_to_tensor=False)
                similarity = float(cosine_similarity([text_embedding], [doc_embedding])[0][0])
                
                if similarity > threshold:
                    results.append({
                        'document_id': str(doc.id),
                        'title': doc.title,
                        'similarity': similarity,
                        'details': {'semantic_similarity': similarity}
                    })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    def _detect_ai_patterns(self, text):
        patterns = {
            r'\b(furthermore|moreover|additionally|consequently|nevertheless)\b': 0.08,
            r'\b(it is important to note|it should be noted|it is worth noting)\b': 0.12,
            r'\b(in conclusion|to summarize|in summary|to conclude)\b': 0.08,
            r'\b(various|numerous|several|multiple)\b.*\b(aspects|factors|elements)\b': 0.1,
            r'\b(the purpose of this|the aim of this|the objective of this)\b': 0.08,
            r'\b(can be seen|it can be argued|it is evident that)\b': 0.08,
            r'\b(in today\'s world|in modern society|in contemporary times)\b': 0.08,
            r'\b(plays a crucial role|plays an important role|is essential)\b': 0.08,
            r'\b(has been shown|research shows|studies indicate)\b': 0.08,
        }
        
        import re
        score = 0
        for pattern, weight in patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches * weight
        
        return min(score, 1.0)
