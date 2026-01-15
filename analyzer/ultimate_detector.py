import re
from difflib import SequenceMatcher
import hashlib
from collections import Counter
import math

class UltimatePlagiarismDetector:
    """Ultimate plagiarism detector combining 10+ methods for maximum accuracy"""
    
    def __init__(self):
        self.plagiarism_threshold = 0.25
        self.ai_threshold = 0.45
        self.min_text_length = 10
    
    def detect_all(self, text, documents=None):
        """Comprehensive detection combining plagiarism and AI detection"""
        plagiarism_score = self._detect_plagiarism(text, documents)
        ai_score = self._detect_ai_content(text)
        
        return {
            'plagiarism_score': plagiarism_score,
            'ai_score': ai_score,
            'is_plagiarized': plagiarism_score >= self.plagiarism_threshold,
            'is_ai_generated': ai_score >= self.ai_threshold,
            'overall_risk': max(plagiarism_score, ai_score),
            'details': {
                'plagiarism': self._get_plagiarism_details(text, documents),
                'ai_markers': self._analyze_ai_markers(text),
                'plagiarism_methods': self._get_plagiarism_breakdown(text, documents)
            }
        }
    
    def _detect_plagiarism(self, text, documents=None):
        """Detect plagiarism using 6 methods"""
        if not text or len(text.strip()) < self.min_text_length:
            return 0.0
        
        if not documents:
            return 0.0
        
        max_similarity = 0.0
        for doc in documents:
            if not doc.content or len(doc.content.strip()) < self.min_text_length:
                continue
            
            similarity = self._calculate_plagiarism_similarity(text, doc.content)
            max_similarity = max(max_similarity, similarity)
        
        return max_similarity
    
    def _calculate_plagiarism_similarity(self, text1, text2):
        """Calculate plagiarism using 6 methods"""
        seq = self._sequence_match(text1, text2)
        ngram3 = self._ngram_similarity(text1, text2, n=3)
        ngram4 = self._ngram_similarity(text1, text2, n=4)
        word = self._word_overlap(text1, text2)
        semantic = self._semantic_similarity(text1, text2)
        fuzzy = self._fuzzy_match(text1, text2)
        
        # Weighted: sequence(25%), ngram3(20%), ngram4(20%), word(15%), semantic(15%), fuzzy(5%)
        return (seq * 0.25) + (ngram3 * 0.20) + (ngram4 * 0.20) + (word * 0.15) + (semantic * 0.15) + (fuzzy * 0.05)
    
    def _sequence_match(self, text1, text2):
        """Sequence matching"""
        matcher = SequenceMatcher(None, text1.lower(), text2.lower())
        return matcher.ratio()
    
    def _ngram_similarity(self, text1, text2, n=4):
        """N-gram analysis"""
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
        """Word-level overlap"""
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
        
        common_words = set(freq1.keys()) & set(freq2.keys())
        if not common_words:
            return 0.0
        
        dot_product = sum(freq1[w] * freq2[w] for w in common_words)
        magnitude1 = math.sqrt(sum(v**2 for v in freq1.values()))
        magnitude2 = math.sqrt(sum(v**2 for v in freq2.values()))
        
        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0
        
        return dot_product / (magnitude1 * magnitude2)
    
    def _fuzzy_match(self, text1, text2):
        """Fuzzy matching for typos and variations"""
        text1_words = text1.lower().split()
        text2_words = text2.lower().split()
        
        if not text1_words or not text2_words:
            return 0.0
        
        matches = 0
        for w1 in text1_words[:50]:
            for w2 in text2_words[:50]:
                if self._string_similarity(w1, w2) > 0.85:
                    matches += 1
                    break
        
        return matches / max(len(text1_words), len(text2_words))
    
    def _string_similarity(self, s1, s2):
        """Calculate string similarity"""
        if len(s1) < 3 or len(s2) < 3:
            return 1.0 if s1 == s2 else 0.0
        
        matcher = SequenceMatcher(None, s1, s2)
        return matcher.ratio()
    
    def _detect_ai_content(self, text):
        """Detect AI-generated content using 10 markers"""
        if not text or len(text.strip()) < self.min_text_length:
            return 0.0
        
        markers = self._analyze_ai_markers(text)
        
        weights = {
            'formal_transitions': 0.15,
            'repetitive_structure': 0.15,
            'passive_voice': 0.12,
            'hedging_language': 0.12,
            'complexity': 0.12,
            'vocabulary_diversity': 0.10,
            'conclusion_markers': 0.08,
            'sentence_length_variance': 0.08,
            'punctuation_patterns': 0.05,
            'rare_word_usage': 0.03
        }
        
        ai_score = sum(markers.get(key, 0) * weight for key, weight in weights.items())
        return min(ai_score, 1.0)
    
    def _analyze_ai_markers(self, text):
        """Analyze 10 AI markers"""
        text_lower = text.lower()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        markers = {}
        
        # 1. Formal transitions
        formal_transitions = ['furthermore', 'moreover', 'in addition', 'consequently', 
                            'therefore', 'thus', 'hence', 'additionally', 'notably',
                            'significantly', 'importantly', 'ultimately', 'essentially']
        transition_count = sum(text_lower.count(t) for t in formal_transitions)
        markers['formal_transitions'] = min(transition_count / max(len(sentences), 1) * 0.5, 1.0)
        
        # 2. Repetitive structure
        if len(sentences) > 3:
            sentence_starts = [s.split()[0] if s.split() else '' for s in sentences]
            start_counter = Counter(sentence_starts)
            repetition = max(start_counter.values()) / len(sentences) if sentences else 0
            markers['repetitive_structure'] = min(repetition * 0.8, 1.0)
        else:
            markers['repetitive_structure'] = 0.0
        
        # 3. Passive voice
        passive_pattern = r'\b(is|are|was|were|be|been|being)\s+\w+ed\b'
        passive_count = len(re.findall(passive_pattern, text_lower))
        markers['passive_voice'] = min(passive_count / max(len(sentences), 1) * 0.6, 1.0)
        
        # 4. Hedging language
        hedging_words = ['may', 'might', 'could', 'possibly', 'arguably', 'somewhat',
                        'relatively', 'rather', 'quite', 'seems', 'appears', 'tends']
        hedging_count = sum(len(re.findall(r'\b' + word + r'\b', text_lower)) for word in hedging_words)
        markers['hedging_language'] = min(hedging_count / max(len(sentences), 1) * 0.4, 1.0)
        
        # 5. Complexity
        avg_word_length = sum(len(word) for word in text.split()) / max(len(text.split()), 1)
        avg_sentence_length = len(text.split()) / max(len(sentences), 1)
        complexity = (avg_word_length / 6.0) * 0.5 + (avg_sentence_length / 20.0) * 0.5
        markers['complexity'] = min(complexity, 1.0)
        
        # 6. Vocabulary diversity
        words = re.findall(r'\b\w+\b', text_lower)
        unique_words = len(set(words))
        diversity = unique_words / max(len(words), 1)
        markers['vocabulary_diversity'] = min(diversity * 1.5, 1.0)
        
        # 7. Conclusion markers
        conclusion_markers = ['in conclusion', 'to conclude', 'in summary', 'to summarize',
                            'ultimately', 'in essence', 'in short']
        conclusion_count = sum(text_lower.count(m) for m in conclusion_markers)
        markers['conclusion_markers'] = min(conclusion_count * 0.3, 1.0)
        
        # 8. Sentence length variance
        if len(sentences) > 1:
            sentence_lengths = [len(s.split()) for s in sentences]
            avg_length = sum(sentence_lengths) / len(sentence_lengths)
            variance = sum((l - avg_length) ** 2 for l in sentence_lengths) / len(sentence_lengths)
            std_dev = math.sqrt(variance)
            markers['sentence_length_variance'] = min(std_dev / 10.0, 1.0)
        else:
            markers['sentence_length_variance'] = 0.0
        
        # 9. Punctuation patterns
        punctuation_count = len(re.findall(r'[,;:]', text))
        markers['punctuation_patterns'] = min(punctuation_count / max(len(sentences), 1) * 0.3, 1.0)
        
        # 10. Rare word usage
        rare_words = ['aforementioned', 'notwithstanding', 'heretofore', 'henceforth',
                     'erstwhile', 'perchance', 'betwixt', 'thenceforth']
        rare_count = sum(text_lower.count(w) for w in rare_words)
        markers['rare_word_usage'] = min(rare_count * 0.2, 1.0)
        
        return markers
    
    def _get_plagiarism_details(self, text, documents):
        """Get detailed plagiarism analysis"""
        if not documents:
            return {'status': 'no_documents', 'matches': []}
        
        results = []
        for doc in documents:
            if not doc.content or len(doc.content.strip()) < self.min_text_length:
                continue
            
            similarity = self._calculate_plagiarism_similarity(text, doc.content)
            if similarity >= self.plagiarism_threshold:
                results.append({
                    'title': doc.title,
                    'similarity': similarity,
                    'sequence': self._sequence_match(text, doc.content),
                    'ngram3': self._ngram_similarity(text, doc.content, n=3),
                    'ngram4': self._ngram_similarity(text, doc.content, n=4),
                    'word_overlap': self._word_overlap(text, doc.content)
                })
        
        return {
            'status': 'plagiarized' if results else 'original',
            'matches': sorted(results, key=lambda x: x['similarity'], reverse=True)
        }
    
    def _get_plagiarism_breakdown(self, text, documents):
        """Get breakdown of plagiarism detection methods"""
        if not documents or not documents.exists():
            return {}
        
        doc = documents.first()
        if not doc.content:
            return {}
        
        return {
            'sequence_match': self._sequence_match(text, doc.content),
            'ngram_3gram': self._ngram_similarity(text, doc.content, n=3),
            'ngram_4gram': self._ngram_similarity(text, doc.content, n=4),
            'word_overlap': self._word_overlap(text, doc.content),
            'semantic': self._semantic_similarity(text, doc.content),
            'fuzzy_match': self._fuzzy_match(text, doc.content)
        }
    
    def get_fingerprint(self, text):
        """Generate document fingerprint"""
        return hashlib.sha256(text.lower().encode()).hexdigest()
