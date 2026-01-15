import re
from difflib import SequenceMatcher
import hashlib
import math

class ProfessionalPlagiarismDetector:
    """Industry-standard plagiarism detection using multiple algorithms"""
    
    def detect_plagiarism(self, text, documents=None, threshold=0.3):
        results = []
        
        # Database comparison (primary method)
        if documents:
            for doc in documents:
                similarity = self._advanced_similarity(text, doc.content)
                if similarity > threshold:
                    results.append({
                        'document_id': str(doc.id),
                        'title': doc.title,
                        'similarity': similarity,
                        'details': {
                            'sequence_match': self._sequence_match(text, doc.content),
                            'ngram_match': self._ngram_similarity(text, doc.content),
                            'word_overlap': self._word_overlap(text, doc.content)
                        }
                    })
        
        # If no high matches, return results with pattern analysis
        if not results or max([r['similarity'] for r in results], default=0) < 0.5:
            results.append({
                'document_id': 'analysis',
                'title': 'Text Analysis',
                'similarity': 0.0,
                'details': {'note': 'No plagiarism detected in database'}
            })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    def _advanced_similarity(self, text1, text2):
        """Calculate advanced similarity using multiple methods"""
        seq = self._sequence_match(text1, text2)
        ngram = self._ngram_similarity(text1, text2)
        word = self._word_overlap(text1, text2)
        
        # Weighted average: sequence(50%), ngram(30%), word(20%)
        return (seq * 0.5) + (ngram * 0.3) + (word * 0.2)
    
    def _sequence_match(self, text1, text2):
        """Sequence matching for exact/near-exact plagiarism"""
        matcher = SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()
    
    def _ngram_similarity(self, text1, text2, n=4):
        """N-gram analysis for phrase-level plagiarism"""
        def get_ngrams(text):
            words = text.lower().split()
            return set(' '.join(words[i:i+n]) for i in range(max(0, len(words)-n+1)))
        
        ngrams1 = get_ngrams(text1)
        ngrams2 = get_ngrams(text2)
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)
        return intersection / union if union > 0 else 0.0
    
    def _word_overlap(self, text1, text2):
        """Word-level overlap detection"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0
    
    def get_fingerprint(self, text):
        """Generate document fingerprint for fast comparison"""
        return hashlib.sha256(text.lower().encode()).hexdigest()
