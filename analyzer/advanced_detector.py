import re
from collections import Counter
import math
from difflib import SequenceMatcher

class AdvancedPlagiarismDetector:
    def detect_plagiarism(self, text, documents=None, threshold=0.3):
        results = []
        
        # Semantic plagiarism detection
        semantic_score = self._semantic_analysis(text)
        results.append({
            'document_id': 'semantic_analysis',
            'title': 'Semantic Plagiarism Detection',
            'similarity': semantic_score,
            'details': {'semantic_score': semantic_score}
        })
        
        # Pattern-based detection
        pattern_score = self._pattern_analysis(text)
        results.append({
            'document_id': 'pattern_analysis',
            'title': 'Pattern Analysis',
            'similarity': pattern_score,
            'details': {'pattern_score': pattern_score}
        })
        
        # Linguistic fingerprint
        fingerprint_score = self._linguistic_fingerprint(text)
        results.append({
            'document_id': 'linguistic_fingerprint',
            'title': 'Linguistic Fingerprint',
            'similarity': fingerprint_score,
            'details': {'fingerprint_score': fingerprint_score}
        })
        
        # Check against database documents if provided
        if documents:
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
    
    def _semantic_analysis(self, text):
        score = 0.0
        
        # Check for copied phrases and common expressions
        copied_phrases = [
            r'\b(in conclusion|to summarize|in summary|as mentioned|as stated|as discussed)\b',
            r'\b(it is important|it is evident|it is clear|it is obvious)\b',
            r'\b(furthermore|moreover|additionally|consequently|nevertheless)\b',
            r'\b(can be seen|can be found|can be observed|can be noted)\b',
        ]
        
        phrase_count = 0
        for phrase in copied_phrases:
            phrase_count += len(re.findall(phrase, text, re.I))
        
        score += min(phrase_count * 0.08, 0.35)
        
        # Check for unnatural transitions
        words = text.lower().split()
        if len(words) > 20:
            bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words)-1)]
            unique_bigrams = len(set(bigrams)) / len(bigrams) if bigrams else 1
            if unique_bigrams > 0.92:
                score += 0.15
        
        return min(score, 1.0)
    
    def _pattern_analysis(self, text):
        score = 0.0
        
        # Sentence structure analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) > 5:
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            
            # Unnatural consistency in sentence length
            variance = sum((x - avg_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
            if variance < 5:
                score += 0.2
        
        # Check for repetitive structures
        sentence_starts = [re.match(r'^(\w+)', s) for s in sentences]
        starts = [m.group(1).lower() for m in sentence_starts if m]
        
        if starts:
            start_freq = Counter(starts)
            max_freq = max(start_freq.values())
            if max_freq / len(starts) > 0.3:
                score += 0.15
        
        # Passive voice overuse
        passive_count = len(re.findall(r'\b(is|are|was|were)\s+\w+ed\b', text, re.I))
        if passive_count > len(sentences) * 0.4:
            score += 0.15
        
        return min(score, 1.0)
    
    def _linguistic_fingerprint(self, text):
        score = 0.0
        
        # Vocabulary complexity
        words = text.lower().split()
        unique_words = len(set(words))
        word_diversity = unique_words / len(words) if words else 0
        
        if word_diversity < 0.4:
            score += 0.2
        
        # Check for AI markers
        ai_markers = len(re.findall(
            r'\b(in conclusion|to summarize|it is important|can be seen|it is evident|'
            r'furthermore|moreover|additionally|consequently|nevertheless|'
            r'as mentioned|as stated|as discussed|in summary)\b',
            text, re.I
        ))
        score += min(ai_markers * 0.06, 0.25)
        
        # Punctuation patterns
        punctuation_ratio = len(re.findall(r'[,;:]', text)) / len(text) if text else 0
        if punctuation_ratio > 0.05:
            score += 0.1
        
        # Check for quoted material patterns
        quoted = len(re.findall(r'["\'].*?["\']', text))
        if quoted > len(sentences := re.split(r'[.!?]+', text)) * 0.3:
            score += 0.15
        
        return min(score, 1.0)
    
    def _compare_texts(self, text1, text2):
        matcher = SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()
