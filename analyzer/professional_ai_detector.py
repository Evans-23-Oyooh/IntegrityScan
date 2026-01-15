import re
from collections import Counter
import math

class ProfessionalAIDetector:
    """Professional AI content detection using linguistic analysis"""
    
    def detect_ai_content(self, text):
        """Detect AI-generated content (0.0 to 1.0)"""
        if not text or len(text.strip()) < 50:
            return 0.0
        
        scores = []
        
        # 1. Formal transition phrases (20%)
        formal_score = self._detect_formal_transitions(text)
        scores.append(('formal_transitions', formal_score, 0.20))
        
        # 2. Repetitive sentence structure (20%)
        structure_score = self._detect_repetitive_structure(text)
        scores.append(('sentence_structure', structure_score, 0.20))
        
        # 3. Passive voice overuse (15%)
        passive_score = self._detect_passive_voice(text)
        scores.append(('passive_voice', passive_score, 0.15))
        
        # 4. Hedging language (15%)
        hedging_score = self._detect_hedging_language(text)
        scores.append(('hedging_language', hedging_score, 0.15))
        
        # 5. Complex sentence patterns (15%)
        complexity_score = self._detect_complexity(text)
        scores.append(('complexity', complexity_score, 0.15))
        
        # 6. Vocabulary diversity (10%)
        diversity_score = self._detect_vocabulary_diversity(text)
        scores.append(('vocabulary_diversity', diversity_score, 0.10))
        
        # 7. Conclusion markers (5%)
        conclusion_score = self._detect_conclusion_markers(text)
        scores.append(('conclusion_markers', conclusion_score, 0.05))
        
        # Calculate weighted average
        total_score = sum(score * weight for _, score, weight in scores)
        return min(max(total_score, 0.0), 1.0)
    
    def _detect_formal_transitions(self, text):
        """Detect formal transition phrases (20%)"""
        transitions = [
            r'\b(furthermore|moreover|additionally|consequently|nevertheless|'
            r'notwithstanding|in addition|as a result|therefore|thus|hence)\b',
            r'\b(in conclusion|to summarize|in summary|as mentioned|as stated|'
            r'as discussed|in essence|ultimately)\b'
        ]
        
        count = sum(len(re.findall(phrase, text, re.I)) for phrase in transitions)
        sentences = len(re.split(r'[.!?]+', text))
        
        if sentences == 0:
            return 0.0
        
        ratio = count / sentences
        return min(ratio / 0.3, 1.0)  # Normalize to 1.0 at 0.3 ratio
    
    def _detect_repetitive_structure(self, text):
        """Detect repetitive sentence structures (20%)"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if len(sentences) < 3:
            return 0.0
        
        # Check sentence length consistency
        lengths = [len(s.split()) for s in sentences]
        avg_length = sum(lengths) / len(lengths)
        variance = sum((x - avg_length) ** 2 for x in lengths) / len(lengths)
        
        # Low variance = repetitive
        if variance < 10:
            return 0.7
        elif variance < 20:
            return 0.4
        else:
            return 0.1
    
    def _detect_passive_voice(self, text):
        """Detect passive voice overuse (15%)"""
        passive_pattern = r'\b(is|are|was|were|be|been|being)\s+\w+ed\b'
        passive_count = len(re.findall(passive_pattern, text, re.I))
        
        sentences = len(re.split(r'[.!?]+', text))
        if sentences == 0:
            return 0.0
        
        ratio = passive_count / sentences
        return min(ratio / 0.4, 1.0)  # Normalize to 1.0 at 0.4 ratio
    
    def _detect_hedging_language(self, text):
        """Detect hedging/uncertain language (15%)"""
        hedging = [
            r'\b(may|might|could|possibly|perhaps|arguably|seems|appears|'
            r'tends to|appears to|seems to|it could be|it might be)\b'
        ]
        
        count = sum(len(re.findall(phrase, text, re.I)) for phrase in hedging)
        words = len(text.split())
        
        if words == 0:
            return 0.0
        
        ratio = count / words
        return min(ratio / 0.05, 1.0)  # Normalize to 1.0 at 5% ratio
    
    def _detect_complexity(self, text):
        """Detect overly complex sentence patterns (15%)"""
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        if not sentences:
            return 0.0
        
        # Count complex sentences (with multiple clauses)
        complex_count = 0
        for sentence in sentences:
            if sentence.count(',') >= 2 or sentence.count(';') >= 1:
                complex_count += 1
        
        ratio = complex_count / len(sentences)
        return min(ratio / 0.5, 1.0)  # Normalize to 1.0 at 50% complex
    
    def _detect_vocabulary_diversity(self, text):
        """Detect low vocabulary diversity (10%)"""
        words = text.lower().split()
        if not words:
            return 0.0
        
        unique_words = len(set(words))
        diversity = unique_words / len(words)
        
        # Low diversity = AI-like
        if diversity < 0.4:
            return 0.8
        elif diversity < 0.5:
            return 0.5
        elif diversity < 0.6:
            return 0.2
        else:
            return 0.0
    
    def _detect_conclusion_markers(self, text):
        """Detect conclusion markers (5%)"""
        markers = [
            r'\b(in conclusion|to conclude|in summary|to summarize|'
            r'in essence|ultimately|finally|in the end)\b'
        ]
        
        count = sum(len(re.findall(marker, text, re.I)) for marker in markers)
        return min(count * 0.2, 1.0)
    
    def get_ai_probability(self, text):
        """Get AI probability as percentage"""
        return self.detect_ai_content(text)
