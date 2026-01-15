import re
from collections import Counter
import math

class UltraAccuratePlagiarismDetector:
    def detect_plagiarism(self, text, documents, threshold=0.7):
        results = []
        
        # Analyze text for plagiarism indicators
        plagiarism_score = self._analyze_text_patterns(text)
        
        results.append({
            'document_id': 'pattern_analysis',
            'title': 'Pattern Analysis',
            'similarity': plagiarism_score,
            'details': {'pattern_score': plagiarism_score}
        })
        
        # Check against database documents
        for doc in documents:
            similarity = self._compare_texts(text, doc.content)
            if similarity > threshold:
                results.append({
                    'document_id': str(doc.id),
                    'title': doc.title,
                    'similarity': similarity,
                    'details': {'match_score': similarity}
                })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    def _analyze_text_patterns(self, text):
        score = 0.0
        
        # Check for excessive formal language
        formal_words = len(re.findall(r'\b(furthermore|moreover|additionally|consequently|nevertheless|notwithstanding)\b', text, re.I))
        score += min(formal_words * 0.05, 0.3)
        
        # Check for repetitive sentence structures
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 3:
            sentence_starts = [re.match(r'^[A-Za-z]+', s.strip()) for s in sentences if s.strip()]
            starts = [m.group() for m in sentence_starts if m]
            if starts:
                start_freq = Counter(starts)
                repetition = max(start_freq.values()) / len(starts) if starts else 0
                score += min(repetition * 0.2, 0.2)
        
        # Check for unnatural word transitions
        words = text.lower().split()
        if len(words) > 10:
            transitions = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
            unique_ratio = len(set(transitions)) / len(transitions)
            if unique_ratio > 0.95:
                score += 0.15
        
        # Check for AI markers
        ai_markers = len(re.findall(r'\b(in conclusion|to summarize|it is important|can be seen|it is evident)\b', text, re.I))
        score += min(ai_markers * 0.08, 0.25)
        
        return min(score, 1.0)
    
    def _compare_texts(self, text1, text2):
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
