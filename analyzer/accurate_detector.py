import re
from difflib import SequenceMatcher
from collections import Counter
import math

class AccuratePlagiarismDetector:
    def detect_plagiarism(self, text, documents=None, threshold=0.3):
        results = []
        
        # Check against database documents
        if documents:
            for doc in documents:
                similarity = self._calculate_similarity(text, doc.content)
                results.append({
                    'document_id': str(doc.id),
                    'title': doc.title,
                    'similarity': similarity,
                    'details': {'match_score': similarity}
                })
        
        # If no documents or low similarity, analyze text patterns
        if not results or max([r['similarity'] for r in results]) < 0.5:
            pattern_score = self._detect_ai_patterns(text)
            results.append({
                'document_id': 'pattern_analysis',
                'title': 'AI/Pattern Detection',
                'similarity': pattern_score,
                'details': {'pattern_score': pattern_score}
            })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)
    
    def _calculate_similarity(self, text1, text2):
        # Sequence matching for exact/near-exact plagiarism
        matcher = SequenceMatcher(None, text1.lower(), text2.lower())
        sequence_ratio = matcher.ratio()
        
        # N-gram similarity
        ngram_ratio = self._ngram_similarity(text1, text2)
        
        # Word overlap
        word_ratio = self._word_overlap(text1, text2)
        
        # Weighted average
        similarity = (sequence_ratio * 0.4) + (ngram_ratio * 0.35) + (word_ratio * 0.25)
        return min(similarity, 1.0)
    
    def _ngram_similarity(self, text1, text2, n=3):
        def get_ngrams(text):
            words = text.lower().split()
            return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
        
        ngrams1 = set(get_ngrams(text1))
        ngrams2 = set(get_ngrams(text2))
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1 & ngrams2)
        union = len(ngrams1 | ngrams2)
        return intersection / union if union > 0 else 0.0
    
    def _word_overlap(self, text1, text2):
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        return intersection / union if union > 0 else 0.0
    
    def _detect_ai_patterns(self, text):
        score = 0.0
        
        # AI marker phrases
        ai_markers = [
            r'\b(in conclusion|to summarize|in summary|as mentioned|as stated)\b',
            r'\b(it is important|it is evident|it is clear|it is obvious)\b',
            r'\b(furthermore|moreover|additionally|consequently|nevertheless)\b',
            r'\b(can be seen|can be found|can be observed|can be noted)\b',
        ]
        
        marker_count = sum(len(re.findall(phrase, text, re.I)) for phrase in ai_markers)
        score += min(marker_count * 0.05, 0.3)
        
        # Sentence structure consistency
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) > 5:
            lengths = [len(s.split()) for s in sentences]
            avg = sum(lengths) / len(lengths)
            variance = sum((x - avg) ** 2 for x in lengths) / len(lengths)
            if variance < 8:
                score += 0.2
        
        # Passive voice overuse
        passive = len(re.findall(r'\b(is|are|was|were)\s+\w+ed\b', text, re.I))
        if passive > len(sentences) * 0.35:
            score += 0.15
        
        # Low vocabulary diversity
        words = text.lower().split()
        unique_ratio = len(set(words)) / len(words) if words else 1
        if unique_ratio < 0.45:
            score += 0.15
        
        return min(score, 1.0)
