from .ultra_detector import UltraAccuratePlagiarismDetector
from .services import (AIDetector, TextSummarizationService, SentimentAnalysisService, 
                       TextStatisticsService, URLShortenerService, QRCodeGenerator, KeywordExtractionService)
from .document_parser import DocumentParser

class ToolValidator:
    @staticmethod
    def validate_plagiarism_check(text):
        try:
            detector = UltraAccuratePlagiarismDetector()
            return {'status': 'ok', 'message': 'Plagiarism detector initialized'}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def validate_ai_detection(text):
        try:
            detector = AIDetector()
            result = detector.detect_ai_content(text)
            return {'status': 'ok', 'ai_probability': result['ai_probability']}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def validate_text_summarization(text):
        try:
            service = TextSummarizationService()
            summary = service.extractive_summary(text, num_sentences=3)
            return {'status': 'ok', 'summary_length': len(summary)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def validate_sentiment_analysis(text):
        try:
            service = SentimentAnalysisService()
            result = service.analyze_sentiment(text)
            return {'status': 'ok', 'sentiment': result['sentiment']}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def validate_text_statistics(text):
        try:
            service = TextStatisticsService()
            stats = service.analyze_text(text)
            return {'status': 'ok', 'word_count': stats['word_count']}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def validate_url_shortener(url):
        try:
            is_valid = URLShortenerService.is_valid_url(url)
            return {'status': 'ok', 'is_valid': is_valid}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def validate_qr_generator(content):
        try:
            qr_image = QRCodeGenerator.generate_qr_code(content, 'url')
            return {'status': 'ok', 'qr_generated': True}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    @staticmethod
    def validate_document_parser(file):
        try:
            text = DocumentParser.extract_text_from_file(file)
            return {'status': 'ok', 'text_length': len(text)}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
