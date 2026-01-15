import re
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize, sent_tokenize
import random

class AIHumanizer:
    """Remove AI detection markers to humanize AI-generated content"""
    
    def humanize(self, text):
        """Apply multiple humanization techniques"""
        text = self._reduce_formal_transitions(text)
        text = self._vary_sentence_structure(text)
        text = self._reduce_passive_voice(text)
        text = self._reduce_hedging(text)
        text = self._simplify_complexity(text)
        text = self._add_natural_variations(text)
        text = self._remove_conclusion_markers(text)
        text = self._reduce_punctuation_patterns(text)
        
        return text
    
    def _reduce_formal_transitions(self, text):
        """Replace formal transitions with casual ones"""
        replacements = {
            r'\bfurthermore\b': 'also',
            r'\bmoreover\b': 'plus',
            r'\bin addition\b': 'and',
            r'\bconsequently\b': 'so',
            r'\btherefore\b': 'so',
            r'\bthus\b': 'so',
            r'\bhence\b': 'so',
            r'\badditionally\b': 'also',
            r'\bnotably\b': 'notably',
            r'\bsignificantly\b': 'importantly',
            r'\bimportantly\b': 'importantly',
            r'\bultimately\b': 'finally',
            r'\bessentially\b': 'basically'
        }
        
        for formal, casual in replacements.items():
            text = re.sub(formal, casual, text, flags=re.IGNORECASE)
        
        return text
    
    def _vary_sentence_structure(self, text):
        """Vary sentence starting patterns"""
        sentences = sent_tokenize(text)
        varied = []
        
        for i, sent in enumerate(sentences):
            if i > 0 and random.random() > 0.7:
                words = sent.split()
                if len(words) > 3:
                    random.shuffle(words[:3])
                    sent = ' '.join(words)
            varied.append(sent)
        
        return ' '.join(varied)
    
    def _reduce_passive_voice(self, text):
        """Convert passive to active voice"""
        passive_pattern = r'\b(is|are|was|were|be|been|being)\s+(\w+ed)\s+by\b'
        
        def convert_to_active(match):
            verb = match.group(2)
            return f"did {verb}"
        
        text = re.sub(passive_pattern, convert_to_active, text, flags=re.IGNORECASE)
        
        # Simple passive to active conversion
        text = re.sub(r'\bwas\s+(\w+ed)\b', r'did \1', text, flags=re.IGNORECASE)
        text = re.sub(r'\bwere\s+(\w+ed)\b', r'did \1', text, flags=re.IGNORECASE)
        
        return text
    
    def _reduce_hedging(self, text):
        """Remove hedging language"""
        hedging_words = {
            r'\bmay\b': 'can',
            r'\bmight\b': 'could',
            r'\bpossibly\b': '',
            r'\barguably\b': '',
            r'\bsomewhat\b': '',
            r'\brelatively\b': '',
            r'\brather\b': '',
            r'\bquite\b': '',
            r'\bseems\b': 'is',
            r'\bappears\b': 'is',
            r'\btends\b': 'does'
        }
        
        for hedging, replacement in hedging_words.items():
            text = re.sub(hedging, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _simplify_complexity(self, text):
        """Simplify complex words and structures"""
        complex_words = {
            'aforementioned': 'mentioned',
            'notwithstanding': 'despite',
            'heretofore': 'before',
            'henceforth': 'from now on',
            'erstwhile': 'former',
            'perchance': 'maybe',
            'betwixt': 'between',
            'thenceforth': 'after that',
            'utilize': 'use',
            'facilitate': 'help',
            'implement': 'do',
            'demonstrate': 'show',
            'elucidate': 'explain',
            'substantiate': 'prove'
        }
        
        for complex_word, simple_word in complex_words.items():
            pattern = r'\b' + complex_word + r'\b'
            text = re.sub(pattern, simple_word, text, flags=re.IGNORECASE)
        
        return text
    
    def _add_natural_variations(self, text):
        """Add natural human variations"""
        # Add occasional contractions
        text = re.sub(r'\bwill not\b', "won't", text, flags=re.IGNORECASE)
        text = re.sub(r'\bcan not\b', "can't", text, flags=re.IGNORECASE)
        text = re.sub(r'\bdo not\b', "don't", text, flags=re.IGNORECASE)
        text = re.sub(r'\bdoes not\b', "doesn't", text, flags=re.IGNORECASE)
        text = re.sub(r'\bwould not\b', "wouldn't", text, flags=re.IGNORECASE)
        text = re.sub(r'\bcould not\b', "couldn't", text, flags=re.IGNORECASE)
        
        # Add occasional filler words
        sentences = sent_tokenize(text)
        fillers = ['you know', 'I mean', 'like', 'basically', 'honestly']
        
        for i in range(len(sentences)):
            if random.random() > 0.85 and len(sentences[i].split()) > 5:
                filler = random.choice(fillers)
                sentences[i] = f"{filler}, {sentences[i]}"
        
        return ' '.join(sentences)
    
    def _remove_conclusion_markers(self, text):
        """Remove explicit conclusion markers"""
        conclusion_markers = {
            r'\bin conclusion\b': '',
            r'\bto conclude\b': '',
            r'\bin summary\b': '',
            r'\bto summarize\b': '',
            r'\bin essence\b': '',
            r'\bin short\b': ''
        }
        
        for marker, replacement in conclusion_markers.items():
            text = re.sub(marker, replacement, text, flags=re.IGNORECASE)
        
        return text
    
    def _reduce_punctuation_patterns(self, text):
        """Reduce excessive punctuation patterns"""
        # Reduce multiple semicolons
        text = re.sub(r';{2,}', ';', text)
        
        # Reduce multiple commas
        text = re.sub(r',{2,}', ',', text)
        
        # Add some natural punctuation variation
        text = re.sub(r';\s+', ', ', text, count=random.randint(1, 3))
        
        return text
