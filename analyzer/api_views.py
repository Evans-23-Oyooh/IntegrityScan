from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
from .models import Document, PlagiarismCheck, AIDetection, URLShortener, QRCode, PlagiarismRemoval
from .services import PlagiarismDetector, AIDetector, URLShortenerService, QRCodeGenerator, PlagiarismRemover

@csrf_exempt
@require_http_methods(["POST"])
def plagiarism_check_api(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        threshold = float(data.get('threshold', 0.7))
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        detector = PlagiarismDetector()
        documents = Document.objects.all()
        results = detector.detect_plagiarism(text, documents, threshold)
        
        similarity_score = max([r['similarity'] for r in results]) if results else 0.0
        
        check = PlagiarismCheck.objects.create(
            text=text,
            similarity_score=similarity_score,
            is_plagiarized=similarity_score > threshold,
            matches=results
        )
        
        return JsonResponse({
            'id': str(check.id),
            'similarity_score': similarity_score,
            'is_plagiarized': check.is_plagiarized,
            'matches': results,
            'threshold': threshold
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def plagiarism_removal_api(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        target_similarity = float(data.get('target_similarity', 0.3))
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        # Check original similarity
        detector = PlagiarismDetector()
        documents = Document.objects.all()
        original_results = detector.detect_plagiarism(text, documents, 0.1)
        original_similarity = max([r['similarity'] for r in original_results]) if original_results else 0.0
        
        # Remove plagiarism
        remover = PlagiarismRemover()
        result = remover.remove_plagiarism(text, target_similarity)
        
        # Check new similarity
        new_results = detector.detect_plagiarism(result['processed_text'], documents, 0.1)
        new_similarity = max([r['similarity'] for r in new_results]) if new_results else 0.0
        
        # Save to database
        removal = PlagiarismRemoval.objects.create(
            original_text=text,
            processed_text=result['processed_text'],
            similarity_before=original_similarity,
            similarity_after=new_similarity,
            methods_used=result['methods_used']
        )
        
        return JsonResponse({
            'id': str(removal.id),
            'original_text': text,
            'processed_text': result['processed_text'],
            'similarity_before': original_similarity,
            'similarity_after': new_similarity,
            'improvement': original_similarity - new_similarity,
            'methods_used': result['methods_used']
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def ai_detection_api(request):
    try:
        data = json.loads(request.body)
        text = data.get('text', '')
        
        if not text:
            return JsonResponse({'error': 'Text is required'}, status=400)
        
        detector = AIDetector()
        result = detector.detect_ai_content(text)
        humanized = detector.humanize_text(text) if result['is_ai_generated'] else text
        
        detection = AIDetection.objects.create(
            text=text,
            ai_probability=result['ai_probability'],
            is_ai_generated=result['is_ai_generated'],
            humanized_text=humanized
        )
        
        return JsonResponse({
            'id': str(detection.id),
            'ai_probability': result['ai_probability'],
            'is_ai_generated': result['is_ai_generated'],
            'humanized_text': humanized,
            'confidence': result.get('confidence', result['ai_probability'])
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def shorten_url_api(request):
    try:
        data = json.loads(request.body)
        original_url = data.get('url', '')
        
        if not original_url or not URLShortenerService.is_valid_url(original_url):
            return JsonResponse({'error': 'Valid URL is required'}, status=400)
        
        short_code = URLShortenerService.generate_short_code()
        
        while URLShortener.objects.filter(short_code=short_code).exists():
            short_code = URLShortenerService.generate_short_code()
        
        url_obj = URLShortener.objects.create(
            original_url=original_url,
            short_code=short_code
        )
        
        return JsonResponse({
            'id': str(url_obj.id),
            'original_url': original_url,
            'short_code': short_code,
            'short_url': f"{request.build_absolute_uri('/')}{short_code}",
            'clicks': 0
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def generate_qr_api(request):
    try:
        data = json.loads(request.body)
        qr_type = data.get('qr_type', 'url')
        content = data.get('content', '')
        
        if qr_type == 'vcard':
            name = data.get('name', '')
            phone = data.get('phone', '')
            email = data.get('email', '')
            organization = data.get('organization', '')
            content = QRCodeGenerator.generate_vcard(name, phone, email, organization)
        
        if not content:
            return JsonResponse({'error': 'Content is required'}, status=400)
        
        qr_image = QRCodeGenerator.generate_qr_code(content, qr_type)
        
        qr_obj = QRCode.objects.create(
            qr_type=qr_type,
            content=content,
            image=qr_image
        )
        
        return JsonResponse({
            'id': str(qr_obj.id),
            'qr_type': qr_type,
            'content': content,
            'image_url': request.build_absolute_uri(qr_obj.image.url)
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def add_document_api(request):
    try:
        data = json.loads(request.body)
        title = data.get('title', '')
        content = data.get('content', '')
        
        if not title or not content:
            return JsonResponse({'error': 'Title and content are required'}, status=400)
        
        detector = PlagiarismDetector()
        fingerprint = detector.generate_fingerprint(content)
        
        document = Document.objects.create(
            title=title,
            content=content,
            fingerprint=fingerprint
        )
        
        return JsonResponse({
            'id': str(document.id),
            'title': title,
            'fingerprint': fingerprint,
            'created_at': document.created_at.isoformat()
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)