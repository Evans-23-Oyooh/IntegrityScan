import re
from difflib import SequenceMatcher
import hashlib
from collections import Counter
import math

class HybridPlagiarismDetector:
    """Professional plagiarism detection using hybrid algorithms"""
    
    def __init__(self):
        self.threshold = 0.25
        self.min_text_length = 10
    
    def detect_plagiarism(self, text, documents=None, threshold=None):
        """Detect plagiarism with comprehensive analysis"""
        if threshold is None:
            threshold = self.threshold
        
        if not text or len(text.strip()) < self.min_text_length:
            return []
        
        results = []
        
        if documents:
            for doc in documents:
                if not doc.content or len(doc.content.strip()) < self.min_text_length:
                    continue
                
                similarity = self._calculate_similarity(text, doc.content)
                
                if similarity >= threshold:
                    results.append({
                        'document_id': str(doc.id),
                        'title': doc.title,
                        'similarity': similarity,
                        'details': {
                            'sequence_match': self._sequence_match(text, doc.content),
                            'ngram_match': self._ngram_similarity(text, doc.content),
                            'word_overlap': self._word_overlap(text, doc.content),
                            'semantic_similarity': self._semantic_similarity(text, doc.content)
                        }
                    })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    def _calculate_similarity(self, text1, text2):
        """Calculate weighted similarity score"""
        seq = self._sequence_match(text1, text2)
        ngram = self._ngram_similarity(text1, text2)
        word = self._word_overlap(text1, text2)
        semantic = self._semantic_similarity(text1, text2)
        
        # Weighted average: sequence(35%), ngram(30%), word(20%), semantic(15%)
        return (seq * 0.35) + (ngram * 0.30) + (word * 0.20) + (semantic * 0.15)
    
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
    
    def _semantic_similarity(self, text1, text2):
        """Semantic similarity using word frequency"""
        def get_word_freq(text):
            words = re.findall(r'\b\w+\b', text.lower())
            return Counter(words)
        
        freq1 = get_word_freq(text1)
        freq2 = get_word_freq(text2)
        
        if not freq1 or not freq2:
            return 0.0
        
        # Calculate cosine similarity
        common_words = set(freq1.keys()) & set(freq2.keys())
        if not common_words:
            return 0.0
        
        dot_product = sum(freq1[w] * freq2[w] for w in common_words)
        magnitude1 = math.sqrt(sum(v**2 for v in freq1.values()))
        magnitude2 = math.sqrt(sum(v**2 for v in freq2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def get_fingerprint(self, text):
        """Generate document fingerprint for fast comparison"""
        return hashlib.sha256(text.lower().encode()).hexdigest()
    
    def get_detailed_report(self, text, documents=None):
        """Generate detailed plagiarism report"""
        results = self.detect_plagiarism(text, documents, self.threshold)
        
        if not results:
            return {
                'status': 'clean',
                'plagiarism_percentage': 0.0,
                'matches': [],
                'recommendation': 'No plagiarism detected'
            }
        
        max_similarity = max([r['similarity'] for r in results], default=0.0)
        
        status = 'clean' if max_similarity < 0.3 else 'suspicious' if max_similarity < 0.6 else 'plagiarized'
        
        return {
            'status': status,
            'plagiarism_percentage': max_similarity * 100,
            'matches': results,
            'recommendation': self._get_recommendation(max_similarity)
        }
    
    def _get_recommendation(self, similarity):
        """Get recommendation based on similarity score"""
        if similarity < 0.3:
            return 'Text appears to be original'
        elif similarity < 0.6:
            return 'Text shows some similarity - review recommended'
        else:
            return 'Text shows high similarity - plagiarism likely'
