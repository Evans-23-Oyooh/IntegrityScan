import re

class ImprovedAIDetector:
    def __init__(self):
        self.ai_patterns = {
            r'\b(furthermore|moreover|additionally|consequently|nevertheless)\b': 0.08,
            r'\b(it is important to note|it should be noted|it is worth noting)\b': 0.12,
            r'\b(in conclusion|to summarize|in summary|to conclude)\b': 0.08,
            r'\b(various|numerous|several|multiple)\b.*\b(aspects|factors|elements|considerations)\b': 0.1,
            r'\b(the purpose of this|the aim of this|the objective of this)\b': 0.08,
            r'\b(can be seen|it can be argued|it is evident that)\b': 0.08,
            r'\b(in today\'s world|in modern society|in contemporary times)\b': 0.08,
            r'\b(plays a crucial role|plays an important role|is essential)\b': 0.08,
            r'\b(has been shown|research shows|studies indicate)\b': 0.08,
            r'\b(on the other hand|conversely|in contrast)\b': 0.06,
            r'\b(therefore|thus|hence)\b': 0.05,
            r'\b(in addition|furthermore|additionally)\b': 0.05,
            r'\b(it is clear that|it is obvious that)\b': 0.08,
            r'\b(one can see|one might argue)\b': 0.08,
            r'\b(as mentioned|as stated|as discussed)\b': 0.06,
            r'\b(in fact|indeed|in reality)\b': 0.05,
            r'\b(ultimately|finally|in the end)\b': 0.06,
        }
    
    def detect_ai_content(self, text):
        score = 0
        matches_found = {}
        
        for pattern, weight in self.ai_patterns.items():
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            if matches > 0:
                matches_found[pattern] = matches
                score += matches * weight
        
        ai_prob = min(score, 1.0)
        
        return {
            'ai_probability': ai_prob,
            'is_ai_generated': ai_prob > 0.25,
            'confidence': ai_prob,
            'patterns_found': len(matches_found),
            'total_matches': sum(matches_found.values())
        }
