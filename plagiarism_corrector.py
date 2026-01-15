import re
import random
from transformers import pipeline, T5Tokenizer, T5ForConditionalGeneration
import nltk
from nltk.corpus import wordnet
from nltk.tokenize import sent_tokenize, word_tokenize

class PlagiarismCorrector:
    def __init__(self):
        self.paraphraser = pipeline("text2text-generation", model="t5-small")
        self.synonyms_cache = {}
        self._download_nltk_data()
    
    def _download_nltk_data(self):
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
    
    def get_synonyms(self, word):
        if word in self.synonyms_cache:
            return self.synonyms_cache[word]
        
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonyms.add(lemma.name().replace('_', ' '))
        
        synonyms.discard(word)
        self.synonyms_cache[word] = list(synonyms)
        return list(synonyms)
    
    def synonym_replacement(self, text, replacement_rate=0.3):
        words = word_tokenize(text)
        new_words = []
        
        for word in words:
            if random.random() < replacement_rate and word.isalpha():
                synonyms = self.get_synonyms(word.lower())
                if synonyms:
                    new_words.append(random.choice(synonyms))
                else:
                    new_words.append(word)
            else:
                new_words.append(word)
        
        return ' '.join(new_words)
    
    def sentence_restructure(self, text):
        sentences = sent_tokenize(text)
        restructured = []
        
        for sentence in sentences:
            # Simple restructuring patterns
            if sentence.startswith("The "):
                restructured.append(sentence.replace("The ", "A ", 1))
            elif " is " in sentence:
                parts = sentence.split(" is ", 1)
                if len(parts) == 2:
                    restructured.append(f"{parts[1].rstrip('.')} characterizes {parts[0].lower()}.")
                else:
                    restructured.append(sentence)
            else:
                restructured.append(sentence)
        
        return ' '.join(restructured)
    
    def paraphrase_with_t5(self, text):
        try:
            # Split into sentences for better processing
            sentences = sent_tokenize(text)
            paraphrased_sentences = []
            
            for sentence in sentences:
                if len(sentence.split()) > 3:  # Only paraphrase longer sentences
                    prompt = f"paraphrase: {sentence}"
                    result = self.paraphraser(prompt, max_length=100, num_return_sequences=1)
                    paraphrased_sentences.append(result[0]['generated_text'])
                else:
                    paraphrased_sentences.append(sentence)
            
            return ' '.join(paraphrased_sentences)
        except:
            return text
    
    def active_to_passive(self, text):
        # Simple active to passive voice conversion
        patterns = [
            (r'(\w+) (\w+ed) (\w+)', r'\3 was \2 by \1'),
            (r'(\w+) (\w+s) (\w+)', r'\3 is \2 by \1'),
            (r'(\w+) will (\w+) (\w+)', r'\3 will be \2 by \1')
        ]
        
        result = text
        for pattern, replacement in patterns:
            result = re.sub(pattern, replacement, result)
        
        return result
    
    def correct_plagiarism(self, text, methods=['synonym', 'restructure', 'paraphrase']):
        corrected_versions = {}
        
        if 'synonym' in methods:
            corrected_versions['synonym_replacement'] = self.synonym_replacement(text)
        
        if 'restructure' in methods:
            corrected_versions['sentence_restructure'] = self.sentence_restructure(text)
        
        if 'paraphrase' in methods:
            corrected_versions['ai_paraphrase'] = self.paraphrase_with_t5(text)
        
        if 'voice_change' in methods:
            corrected_versions['voice_change'] = self.active_to_passive(text)
        
        # Combined approach
        combined = text
        if 'synonym' in methods:
            combined = self.synonym_replacement(combined, 0.2)
        if 'restructure' in methods:
            combined = self.sentence_restructure(combined)
        
        corrected_versions['combined'] = combined
        
        return corrected_versions
    
    def suggest_improvements(self, original_text, plagiarized_parts):
        suggestions = []
        
        for part in plagiarized_parts:
            corrections = self.correct_plagiarism(part['plagiarized_content'])
            suggestions.append({
                'original': part['plagiarized_content'],
                'source': part['source'],
                'similarity': part['similarity'],
                'corrections': corrections
            })
        
        return suggestions