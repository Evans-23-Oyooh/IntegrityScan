import re
from collections import Counter
import math

class AccurateAIDetector:
    def detect_ai_content(self, text):
        score = 0.0
        
        # 1. Formal transition words (20%)
        formal_transitions = len(re.findall(r'\b(furthermore|moreover|additionally|consequently|nevertheless|notwithstanding|in addition|on the other hand)\b', text, re.I))
        score += min(formal_transitions * 0.02, 0.2)
        
        # 2. Academic phrases (20%)
        academic = len(re.findall(r'\b(it is important to note|it should be noted|it is worth noting|can be seen|it is evident|it is clear|one might argue|it can be argued)\b', text, re.I))
        score += min(academic * 0.025, 0.2)
        
        # 3. Conclusion markers (15%)
        conclusions = len(re.findall(r'\b(in conclusion|to summarize|in summary|to conclude|in closing|finally|ultimately)\b', text, re.I))
        score += min(conclusions * 0.025, 0.15)
        
        # 4. Passive voice overuse (15%)
        passive = len(re.findall(r'\b(is|are|was|were)\s+\w+ed\b', text, re.I))
        total_words = len(text.split())
        if total_words > 0:
            passive_ratio = passive / (total_words / 100)
            score += min(passive_ratio * 0.01, 0.15)
        
        # 5. Repetitive sentence structure (15%)
        sentences = re.split(r'[.!?]+', text)
        if len(sentences) > 3:
            sentence_lengths = [len(s.split()) for s in sentences if s.strip()]
            if sentence_lengths:
                avg_length = sum(sentence_lengths) / len(sentence_lengths)
                variance = sum((x - avg_length) ** 2 for x in sentence_lengths) / len(sentence_lengths)
                if variance < 5:
                    score += 0.15
        
        # 6. Hedging language (10%)
        hedging = len(re.findall(r'\b(may|might|could|appears|seems|suggests|indicates|tends|arguably)\b', text, re.I))
        score += min(hedging * 0.01, 0.1)
        
        # 7. Complex sentence structures (5%)
        complex_sentences = len(re.findall(r',.*,', text))
        score += min(complex_sentences * 0.005, 0.05)
        
        return min(score, 1.0)
    
    def humanize_text(self, text):
        replacements = {
            r'\bfurthermore\b': 'also',
            r'\bmoreover\b': 'plus',
            r'\badditionally\b': 'and',
            r'\bconsequently\b': 'so',
            r'\bnevertheless\b': 'but',
            r'\bit is important to note that\b': 'note that',
            r'\bin conclusion\b': 'finally',
            r'\bto summarize\b': 'in short',
            r'\bvarious\b': 'many',
            r'\bnumerous\b': 'many',
            r'\bseveral\b': 'some',
        }
        
        humanized = text
        for pattern, replacement in replacements.items():
            humanized = re.sub(pattern, replacement, humanized, flags=re.IGNORECASE)
        
        return humanized
