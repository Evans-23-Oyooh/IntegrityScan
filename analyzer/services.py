import re
import hashlib
import random
import string
from difflib import SequenceMatcher
from collections import Counter
import qrcode
from io import BytesIO
from django.core.files.base import ContentFile
try:
    from transformers import pipeline
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

try:
    import nltk
    from nltk.corpus import wordnet
    from nltk.tokenize import sent_tokenize, word_tokenize
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False
    nltk = None
    wordnet = None
    sent_tokenize = None
    word_tokenize = None

try:
    from textstat import flesch_reading_ease
    TEXTSTAT_AVAILABLE = True
except ImportError:
    TEXTSTAT_AVAILABLE = False
import heapq
import os

# Optional imports for document processing
try:
    import docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

try:
    import PyPDF2
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False

class DocumentParser:
    @staticmethod
    def extract_text_from_file(file):
        """Extract text from various file formats"""
        file_extension = os.path.splitext(file.name)[1].lower()
        
        try:
            if file_extension == '.txt':
                return file.read().decode('utf-8')
            
            elif file_extension == '.pdf':
                if not PDF_AVAILABLE:
                    raise ValueError("PDF processing not available. Please install PyPDF2.")
                return DocumentParser._extract_from_pdf(file)
            
            elif file_extension in ['.doc', '.docx']:
                if not DOCX_AVAILABLE:
                    raise ValueError("Word document processing not available. Please install python-docx.")
                return DocumentParser._extract_from_docx(file)
            
            elif file_extension in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
                if not OCR_AVAILABLE:
                    raise ValueError("Image processing not available. Please install Pillow and pytesseract.")
                return DocumentParser._extract_from_image(file)
            
            else:
                raise ValueError(f"Unsupported file format: {file_extension}")
                
        except Exception as e:
            raise ValueError(f"Error processing file: {str(e)}")
    
    @staticmethod
    def _extract_from_pdf(file):
        """Extract text from PDF file"""
        text = ""
        try:
            file.seek(0)
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n"
        except Exception as e:
            raise ValueError(f"Error reading PDF: {str(e)}")
        
        if not text.strip():
            raise ValueError("No text found in PDF file")
        
        return text.strip()
    
    @staticmethod
    def _extract_from_docx(file):
        """Extract text from DOCX file"""
        try:
            file.seek(0)
            doc = docx.Document(file)
            text = ""
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text += paragraph.text + "\n"
        except Exception as e:
            raise ValueError(f"Error reading DOCX: {str(e)}")
        
        if not text.strip():
            raise ValueError("No text found in document")
        
        return text.strip()
    
    @staticmethod
    def _extract_from_image(file):
        """Extract text from image using OCR"""
        try:
            image = Image.open(file)
            text = pytesseract.image_to_string(image)
        except Exception as e:
            raise ValueError(f"Error reading image: {str(e)}")
        
        if not text.strip():
            raise ValueError("No text found in image")
        
        return text.strip()
    
    @staticmethod
    def get_supported_formats():
        """Return list of supported file formats"""
        formats = {'text': ['.txt']}
        
        if PDF_AVAILABLE or DOCX_AVAILABLE:
            formats['documents'] = []
            if PDF_AVAILABLE:
                formats['documents'].append('.pdf')
            if DOCX_AVAILABLE:
                formats['documents'].extend(['.doc', '.docx'])
        
        if OCR_AVAILABLE:
            formats['images'] = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        return formats

class PlagiarismDetector:
    def __init__(self):
        self._download_nltk_data()
    
    def _download_nltk_data(self):
        if not NLTK_AVAILABLE:
            return
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet', quiet=True)
        try:
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('punkt_tab', quiet=True)
    
    def preprocess_text(self, text):
        text = re.sub(r'[^\w\s]', '', text.lower())
        words = text.split()
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        return ' '.join([word for word in words if word not in stop_words])
    
    def generate_fingerprint(self, text):
        return hashlib.md5(self.preprocess_text(text).encode()).hexdigest()
    
    def n_gram_similarity(self, text1, text2, n=3):
        def get_ngrams(text, n):
            words = text.split()
            return [' '.join(words[i:i+n]) for i in range(len(words)-n+1)]
        
        ngrams1 = set(get_ngrams(self.preprocess_text(text1), n))
        ngrams2 = set(get_ngrams(self.preprocess_text(text2), n))
        
        if not ngrams1 or not ngrams2:
            return 0.0
        
        intersection = len(ngrams1.intersection(ngrams2))
        union = len(ngrams1.union(ngrams2))
        return intersection / union if union > 0 else 0.0
    
    def word_overlap_similarity(self, text1, text2):
        words1 = set(self.preprocess_text(text1).split())
        words2 = set(self.preprocess_text(text2).split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        return intersection / union if union > 0 else 0.0
    
    def sequence_similarity(self, text1, text2):
        return SequenceMatcher(None, text1, text2).ratio()
    
    def detect_plagiarism(self, text, documents, threshold=0.7):
        results = []
        
        for doc in documents:
            # Multiple similarity algorithms
            similarities = {
                'ngram_3': self.n_gram_similarity(text, doc.content, 3),
                'ngram_4': self.n_gram_similarity(text, doc.content, 4),
                'ngram_5': self.n_gram_similarity(text, doc.content, 5),
                'sequence': self.sequence_similarity(text, doc.content),
                'word_overlap': self.word_overlap_similarity(text, doc.content)
            }
            
            # Weighted combination for better accuracy
            overall_similarity = (
                similarities['ngram_3'] * 0.25 +
                similarities['ngram_4'] * 0.25 +
                similarities['ngram_5'] * 0.20 +
                similarities['sequence'] * 0.20 +
                similarities['word_overlap'] * 0.10
            )
            
            if overall_similarity > threshold:
                results.append({
                    'document_id': str(doc.id),
                    'title': doc.title,
                    'similarity': overall_similarity,
                    'details': similarities
                })
        
        return sorted(results, key=lambda x: x['similarity'], reverse=True)

class AIDetector:
    def __init__(self):
        if TRANSFORMERS_AVAILABLE:
            try:
                self.classifier = pipeline("text-classification", model="roberta-base-openai-detector")
            except:
                self.classifier = None
        else:
            self.classifier = None
    
    def detect_ai_content(self, text):
        if not self.classifier:
            # Fallback heuristic detection
            return self._heuristic_detection(text)
        
        try:
            result = self.classifier(text)
            ai_prob = result[0]['score'] if result[0]['label'] == 'AI' else 1 - result[0]['score']
            return {
                'ai_probability': ai_prob,
                'is_ai_generated': ai_prob > 0.7,
                'confidence': result[0]['score']
            }
        except:
            return self._heuristic_detection(text)
    
    def _heuristic_detection(self, text):
        # Simple heuristic patterns for AI detection
        ai_indicators = [
            r'\b(furthermore|moreover|additionally|consequently)\b',
            r'\b(it is important to note|it should be noted)\b',
            r'\b(in conclusion|to summarize|in summary)\b',
            r'\b(various|numerous|several)\b.*\b(aspects|factors|elements)\b'
        ]
        
        score = 0
        for pattern in ai_indicators:
            matches = len(re.findall(pattern, text, re.IGNORECASE))
            score += matches * 0.1
        
        ai_prob = min(score, 0.9)
        return {
            'ai_probability': ai_prob,
            'is_ai_generated': ai_prob > 0.5,
            'confidence': ai_prob
        }
    
    def humanize_text(self, text):
        # Simple text humanization
        replacements = {
            r'\bfurthermore\b': 'also',
            r'\bmoreover\b': 'plus',
            r'\badditionally\b': 'and',
            r'\bconsequently\b': 'so',
            r'\bit is important to note that\b': 'note that',
            r'\bin conclusion\b': 'finally',
            r'\bvarious\b': 'many',
            r'\bnumerous\b': 'many'
        }
        
        humanized = text
        for pattern, replacement in replacements.items():
            humanized = re.sub(pattern, replacement, humanized, flags=re.IGNORECASE)
        
        return humanized

class URLShortenerService:
    @staticmethod
    def generate_short_code(length=4):
        chars = string.ascii_letters + string.digits
        return ''.join(random.choice(chars) for _ in range(length))
    
    @staticmethod
    def is_valid_url(url):
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return url_pattern.match(url) is not None

class PlagiarismRemover:
    def __init__(self):
        self.detector = PlagiarismDetector()
        self._download_nltk_data()
        self.synonym_cache = {}
    
    def _download_nltk_data(self):
        if not NLTK_AVAILABLE:
            return
        try:
            nltk.data.find('corpora/wordnet')
            nltk.data.find('tokenizers/punkt_tab')
        except LookupError:
            nltk.download('wordnet', quiet=True)
            nltk.download('punkt_tab', quiet=True)
    
    def advanced_paraphrase(self, text):
        if not NLTK_AVAILABLE:
            return text
        sentences = sent_tokenize(text)
        paraphrased = []
        
        for sentence in sentences:
            restructured = self._restructure_sentence(sentence)
            paraphrased.append(restructured)
        
        return ' '.join(paraphrased)
    
    def _restructure_sentence(self, sentence):
        # Multiple restructuring strategies
        strategies = [
            self._passive_to_active,
            self._reorder_clauses,
            self._change_sentence_beginnings,
            self._modify_connectors
        ]
        
        for strategy in strategies:
            sentence = strategy(sentence)
        
        return sentence
    
    def _passive_to_active(self, sentence):
        # Convert passive voice patterns
        patterns = [
            (r'\b(\w+) was (\w+ed) by (\w+)', r'\3 \2 \1'),
            (r'\b(\w+) were (\w+ed) by (\w+)', r'\3 \2 \1'),
            (r'\bis (\w+ed) by', r'involves'),
            (r'\bare (\w+ed) by', r'involve')
        ]
        
        for pattern, replacement in patterns:
            sentence = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
        
        return sentence
    
    def _reorder_clauses(self, sentence):
        # Reorder clauses separated by commas
        if ', ' in sentence and len(sentence.split(', ')) == 2:
            parts = sentence.split(', ')
            if len(parts[0]) > 10 and len(parts[1]) > 10:
                return f"{parts[1]}, {parts[0].lower()}"
        return sentence
    
    def _change_sentence_beginnings(self, sentence):
        # Change common sentence starters
        replacements = {
            r'^The ': 'A ',
            r'^This ': 'Such ',
            r'^These ': 'Such ',
            r'^It is ': 'One finds that ',
            r'^There are ': 'Multiple ',
            r'^In addition': 'Furthermore',
            r'^Moreover': 'Additionally',
            r'^However': 'Nevertheless'
        }
        
        for pattern, replacement in replacements.items():
            sentence = re.sub(pattern, replacement, sentence)
        
        return sentence
    
    def _modify_connectors(self, sentence):
        # Replace connecting words
        connectors = {
            r'\bbecause\b': 'since',
            r'\balthough\b': 'while',
            r'\btherefore\b': 'consequently',
            r'\bhowever\b': 'nevertheless',
            r'\bfurthermore\b': 'additionally',
            r'\bmoreover\b': 'furthermore'
        }
        
        for pattern, replacement in connectors.items():
            sentence = re.sub(pattern, replacement, sentence, flags=re.IGNORECASE)
        
        return sentence
    
    def intelligent_synonym_replacement(self, text, intensity=0.4):
        words = word_tokenize(text)
        new_words = []
        
        for word in words:
            clean_word = re.sub(r'[^a-zA-Z]', '', word.lower())
            
            if (len(clean_word) > 3 and 
                clean_word not in ['this', 'that', 'with', 'from', 'they', 'them', 'have', 'been'] and
                random.random() < intensity):
                
                synonym = self._get_best_synonym(clean_word)
                if synonym:
                    # Preserve original capitalization and punctuation
                    if word[0].isupper():
                        synonym = synonym.capitalize()
                    
                    # Preserve punctuation
                    punctuation = re.findall(r'[^a-zA-Z]', word)
                    if punctuation:
                        synonym += ''.join(punctuation)
                    
                    new_words.append(synonym)
                else:
                    new_words.append(word)
            else:
                new_words.append(word)
        
        return ' '.join(new_words)
    
    def _get_best_synonym(self, word):
        if not NLTK_AVAILABLE:
            return None
        if word in self.synonym_cache:
            return random.choice(self.synonym_cache[word]) if self.synonym_cache[word] else None
        
        synonyms = set()
        for syn in wordnet.synsets(word):
            for lemma in syn.lemmas():
                synonym = lemma.name().replace('_', ' ')
                if (synonym != word and 
                    len(synonym.split()) == 1 and 
                    len(synonym) > 2 and
                    synonym.isalpha()):
                    synonyms.add(synonym)
        
        good_synonyms = [s for s in synonyms if self._is_good_synonym(word, s)]
        self.synonym_cache[word] = good_synonyms[:5]
        
        return random.choice(good_synonyms) if good_synonyms else None
    
    def _is_good_synonym(self, original, synonym):
        # Filter out synonyms that are too different in length or meaning
        length_ratio = len(synonym) / len(original)
        return 0.5 <= length_ratio <= 2.0
    
    def remove_plagiarism(self, text, target_similarity=0.3, max_iterations=5):
        current_text = text
        methods_used = []
        iteration_results = []
        
        for iteration in range(max_iterations):
            # Check current similarity against original
            similarity = self._calculate_similarity(current_text, text)
            iteration_results.append({
                'iteration': iteration + 1,
                'similarity': similarity,
                'text_length': len(current_text)
            })
            
            if similarity <= target_similarity:
                break
            
            # Apply progressive methods
            if iteration == 0:
                current_text = self.intelligent_synonym_replacement(current_text, 0.25)
                methods_used.append('intelligent_synonym_replacement')
            elif iteration == 1:
                current_text = self.advanced_paraphrase(current_text)
                methods_used.append('advanced_paraphrase')
            elif iteration == 2:
                current_text = self.intelligent_synonym_replacement(current_text, 0.4)
                methods_used.append('intensive_synonym_replacement')
            elif iteration == 3:
                current_text = self._sentence_splitting(current_text)
                methods_used.append('sentence_restructuring')
            else:
                current_text = self._final_polish(current_text)
                methods_used.append('final_polish')
        
        final_similarity = self._calculate_similarity(current_text, text)
        
        return {
            'processed_text': current_text,
            'methods_used': methods_used,
            'final_similarity': final_similarity,
            'iterations': len(iteration_results),
            'iteration_details': iteration_results
        }
    
    def _sentence_splitting(self, text):
        if not NLTK_AVAILABLE:
            return text
        sentences = sent_tokenize(text)
        new_sentences = []
        
        for sentence in sentences:
            if len(sentence) > 100 and ' and ' in sentence:
                parts = sentence.split(' and ', 1)
                if len(parts) == 2:
                    new_sentences.append(parts[0] + '.')
                    new_sentences.append(parts[1].capitalize())
                else:
                    new_sentences.append(sentence)
            else:
                new_sentences.append(sentence)
        
        return ' '.join(new_sentences)
    
    def _final_polish(self, text):
        # Final polishing with minor adjustments
        polished = text
        
        # Replace some common academic phrases
        academic_replacements = {
            r'\bin order to\b': 'to',
            r'\bdue to the fact that\b': 'because',
            r'\bin spite of the fact that\b': 'although',
            r'\bfor the purpose of\b': 'to',
            r'\bin the event that\b': 'if'
        }
        
        for pattern, replacement in academic_replacements.items():
            polished = re.sub(pattern, replacement, polished, flags=re.IGNORECASE)
        
        return polished
    
    def _calculate_similarity(self, text1, text2):
        return self.detector.sequence_similarity(text1, text2)

class TextSummarizationService:
    def __init__(self):
        if TRANSFORMERS_AVAILABLE:
            try:
                self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
            except:
                self.summarizer = None
        else:
            self.summarizer = None
    
    def extractive_summary(self, text, num_sentences=3):
        if not NLTK_AVAILABLE:
            return text[:500]
        sentences = sent_tokenize(text)
        if len(sentences) <= num_sentences:
            return text
        
        words = word_tokenize(text.lower())
        word_freq = Counter(words)
        
        sentence_scores = {}
        for sentence in sentences:
            words_in_sentence = word_tokenize(sentence.lower())
            score = sum(word_freq[word] for word in words_in_sentence if word in word_freq)
            sentence_scores[sentence] = score
        
        top_sentences = heapq.nlargest(num_sentences, sentence_scores, key=sentence_scores.get)
        return ' '.join(top_sentences)
    
    def abstractive_summary(self, text, max_length=150):
        if not self.summarizer or len(text) < 100:
            return self.extractive_summary(text)
        
        try:
            summary = self.summarizer(text, max_length=max_length, min_length=30, do_sample=False)
            return summary[0]['summary_text']
        except:
            return self.extractive_summary(text)

class LanguageTranslationService:
    def __init__(self):
        self.languages = {
            'en': 'English', 'es': 'Spanish', 'fr': 'French', 'de': 'German',
            'it': 'Italian', 'pt': 'Portuguese', 'ru': 'Russian', 'zh': 'Chinese',
            'ja': 'Japanese', 'ko': 'Korean', 'ar': 'Arabic', 'hi': 'Hindi'
        }
    
    def translate_text(self, text, target_lang='en', source_lang='auto'):
        # Simple mock translation - in production, use Google Translate API or similar
        translations = {
            'hello': {'es': 'hola', 'fr': 'bonjour', 'de': 'hallo'},
            'world': {'es': 'mundo', 'fr': 'monde', 'de': 'welt'},
            'text': {'es': 'texto', 'fr': 'texte', 'de': 'text'}
        }
        
        # Mock translation for demo
        if target_lang == 'es':
            return f"[Translated to Spanish] {text}"
        elif target_lang == 'fr':
            return f"[Translated to French] {text}"
        else:
            return f"[Translated to {self.languages.get(target_lang, 'Unknown')}] {text}"

class SentimentAnalysisService:
    def __init__(self):
        if TRANSFORMERS_AVAILABLE:
            try:
                self.analyzer = pipeline("sentiment-analysis")
            except:
                self.analyzer = None
        else:
            self.analyzer = None
    
    def analyze_sentiment(self, text):
        if self.analyzer:
            try:
                result = self.analyzer(text)
                sentiment = result[0]['label'].lower()
                confidence = result[0]['score']
                
                return {
                    'sentiment': sentiment,
                    'confidence': confidence,
                    'positive_score': confidence if sentiment == 'positive' else 1 - confidence,
                    'negative_score': confidence if sentiment == 'negative' else 1 - confidence,
                    'neutral_score': 0.5
                }
            except:
                pass
        
        # Fallback simple sentiment analysis
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'disappointing', 'poor']
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = 'positive'
            confidence = min(0.9, 0.5 + (positive_count - negative_count) * 0.1)
        elif negative_count > positive_count:
            sentiment = 'negative'
            confidence = min(0.9, 0.5 + (negative_count - positive_count) * 0.1)
        else:
            sentiment = 'neutral'
            confidence = 0.6
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'positive_score': positive_count / max(len(words), 1),
            'negative_score': negative_count / max(len(words), 1),
            'neutral_score': 1 - (positive_count + negative_count) / max(len(words), 1)
        }

class KeywordExtractionService:
    def extract_keywords(self, text, num_keywords=10):
        if not NLTK_AVAILABLE:
            return []
        words = word_tokenize(text.lower())
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
        
        filtered_words = [word for word in words if word.isalpha() and len(word) > 2 and word not in stop_words]
        word_freq = Counter(filtered_words)
        keywords = [{'word': word, 'frequency': freq} for word, freq in word_freq.most_common(num_keywords)]
        
        return keywords

class TextStatisticsService:
    def analyze_text(self, text):
        if not NLTK_AVAILABLE:
            words = text.split()
            sentences = text.split('.')
        else:
            words = word_tokenize(text)
            sentences = sent_tokenize(text)
        
        paragraphs = text.split('\n\n')
        
        word_count = len([word for word in words if isinstance(word, str) and word.isalpha()])
        character_count = len(text)
        sentence_count = len(sentences)
        paragraph_count = len([p for p in paragraphs if p.strip()])
        
        if TEXTSTAT_AVAILABLE:
            try:
                readability_score = flesch_reading_ease(text)
            except:
                avg_sentence_length = word_count / max(sentence_count, 1)
                readability_score = 206.835 - (1.015 * avg_sentence_length)
        else:
            avg_sentence_length = word_count / max(sentence_count, 1)
            readability_score = 206.835 - (1.015 * avg_sentence_length)
        
        return {
            'word_count': word_count,
            'character_count': character_count,
            'sentence_count': sentence_count,
            'paragraph_count': paragraph_count,
            'readability_score': readability_score,
            'avg_words_per_sentence': word_count / max(sentence_count, 1),
            'avg_characters_per_word': character_count / max(word_count, 1)
        }

class QRCodeGenerator:
    @staticmethod
    def generate_qr_code(content, qr_type='url'):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        return ContentFile(buffer.getvalue(), name=f'qr_{qr_type}.png')
    
    @staticmethod
    def generate_vcard(name, phone, email, organization=''):
        vcard = f"""BEGIN:VCARD
VERSION:3.0
FN:{name}
ORG:{organization}
TEL:{phone}
EMAIL:{email}
END:VCARD"""
        return vcard

class DocumentConverter:
    @staticmethod
    def convert_pdf(file, output_format='pdf'):
        try:
            file.seek(0)
            if output_format == 'pdf':
                content = file.read()
                return {'content': content, 'content_type': 'application/pdf', 'filename': f"{file.name.split('.')[0]}.pdf"}
            elif output_format == 'docx':
                content = file.read()
                return {'content': content, 'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'filename': f"{file.name.split('.')[0]}.docx"}
            elif output_format == 'txt':
                try:
                    import PyPDF2
                    file.seek(0)
                    pdf_reader = PyPDF2.PdfReader(file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() + "\n"
                    return {'content': text.encode('utf-8'), 'content_type': 'text/plain', 'filename': f"{file.name.split('.')[0]}.txt"}
                except Exception as e:
                    return {'content': b'PDF to Text conversion requires PyPDF2', 'content_type': 'text/plain', 'filename': f"{file.name.split('.')[0]}.txt"}
            elif output_format == 'xlsx':
                content = file.read()
                return {'content': content, 'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'filename': f"{file.name.split('.')[0]}.xlsx"}
            elif output_format == 'csv':
                return {'content': b'data,value\nconverted,true', 'content_type': 'text/csv', 'filename': f"{file.name.split('.')[0]}.csv"}
            elif output_format == 'html':
                return {'content': b'<html><body><h1>Converted from PDF</h1></body></html>', 'content_type': 'text/html', 'filename': f"{file.name.split('.')[0]}.html"}
            else:
                raise ValueError(f"Unsupported format: {output_format}")
        except Exception as e:
            raise ValueError(f"PDF conversion error: {str(e)}")
    
    @staticmethod
    def convert_to_pdf(file):
        return {'content': file.read(), 'content_type': 'application/pdf', 'filename': f"{file.name.split('.')[0]}.pdf"}
    
    @staticmethod
    def convert_from_pdf(file):
        return {'content': b'Converted from PDF', 'content_type': 'text/plain', 'filename': f"{file.name.split('.')[0]}.txt"}
    
    @staticmethod
    def convert_to_docx(file):
        return {'content': file.read(), 'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'filename': f"{file.name.split('.')[0]}.docx"}
    
    @staticmethod
    def convert_from_docx(file):
        return {'content': b'Converted from DOCX', 'content_type': 'text/plain', 'filename': f"{file.name.split('.')[0]}.txt"}
    
    @staticmethod
    def convert_to_xlsx(file):
        return {'content': file.read(), 'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'filename': f"{file.name.split('.')[0]}.xlsx"}
    
    @staticmethod
    def convert_from_xlsx(file):
        return {'content': b'Converted from XLSX', 'content_type': 'text/plain', 'filename': f"{file.name.split('.')[0]}.txt"}

class ImageConverter:
    @staticmethod
    def convert_image(file, output_format='png'):
        try:
            from PIL import Image
            img = Image.open(file)
            
            # Convert image format
            buffer = BytesIO()
            img.save(buffer, format=output_format.upper())
            buffer.seek(0)
            
            content_types = {
                'png': 'image/png',
                'jpg': 'image/jpeg',
                'gif': 'image/gif',
                'webp': 'image/webp',
                'bmp': 'image/bmp'
            }
            
            return {
                'content': buffer.getvalue(),
                'content_type': content_types.get(output_format, 'image/png'),
                'filename': f"{file.name.split('.')[0]}.{output_format}"
            }
        except Exception as e:
            raise ValueError(f"Image conversion error: {str(e)}")