from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from django.utils import timezone
import json
from .models import (Document, PlagiarismCheck, AIDetection, URLShortener, QRCode, PlagiarismRemoval,
                    TextSummarization, LanguageTranslation, SentimentAnalysis, KeywordExtraction, TextStatistics, UserProfile)
from .services import (PlagiarismDetector, AIDetector, URLShortenerService, QRCodeGenerator, PlagiarismRemover,
                      TextSummarizationService, LanguageTranslationService, SentimentAnalysisService,
                      KeywordExtractionService, TextStatisticsService)
from .document_parser import DocumentParser
from .decorators import subscription_required
from .ai_humanizer import AIHumanizer
from .ultimate_detector import UltimatePlagiarismDetector

@login_required
def dashboard(request):
    context = {
        'total_documents': Document.objects.count(),
        'total_checks': PlagiarismCheck.objects.count(),
        'total_urls': URLShortener.objects.count(),
        'total_qrcodes': QRCode.objects.count(),
    }
    return render(request, 'dashboard.html', context)

@subscription_required
def plagiarism_check(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        document = request.FILES.get('document')
        threshold = float(request.POST.get('threshold', 0.7))
        
        if document:
            try:
                text = DocumentParser.extract_text_from_file(document)
            except ValueError as e:
                messages.error(request, f'File Error: {str(e)}')
                return render(request, 'plagiarism_check.html')
            except Exception as e:
                messages.error(request, f'Unexpected error: {str(e)}')
                return render(request, 'plagiarism_check.html')
        
        if not text:
            messages.error(request, 'Please provide text or upload a document')
            return render(request, 'plagiarism_check.html')
        
        try:
            detector = UltimatePlagiarismDetector()
            documents = Document.objects.all()
            detection_result = detector.detect_all(text, documents)
            
            plagiarism_score = detection_result['plagiarism_score'] * 100
            ai_score = detection_result['ai_score'] * 100
            overall_risk = detection_result['overall_risk'] * 100
            
            results = detection_result['details']['plagiarism'].get('matches', [])
            for result in results:
                result['similarity'] = result['similarity'] * 100
                for key in ['sequence', 'ngram3', 'ngram4', 'word_overlap']:
                    if key in result:
                        result[key] = result[key] * 100
            
            check = PlagiarismCheck.objects.create(
                text=text,
                similarity_score=plagiarism_score,
                is_plagiarized=plagiarism_score > (threshold * 100),
                matches=results
            )
            
            return render(request, 'plagiarism_result.html', {
                'check': check,
                'results': results,
                'plagiarism_score': plagiarism_score,
                'ai_score': ai_score,
                'overall_risk': overall_risk,
                'ai_markers': detection_result['details']['ai_markers'],
                'plagiarism_methods': detection_result['details']['plagiarism_methods'],
                'threshold': threshold
            })
        except Exception as e:
            messages.error(request, f'Analysis error: {str(e)}')
            return render(request, 'plagiarism_check.html')
    
    return render(request, 'plagiarism_check.html')

@subscription_required
def ai_detection(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        document = request.FILES.get('document')
        
        if document:
            try:
                text = DocumentParser.extract_text_from_file(document)
            except ValueError as e:
                messages.error(request, f'File Error: {str(e)}')
                return render(request, 'ai_detection.html')
            except Exception as e:
                messages.error(request, f'Unexpected error: {str(e)}')
                return render(request, 'ai_detection.html')
        
        if not text:
            messages.error(request, 'Please enter text or upload a document')
            return render(request, 'ai_detection.html')
        
        try:
            detector = UltimatePlagiarismDetector()
            ai_score = detector._detect_ai_content(text)
            ai_markers = detector._analyze_ai_markers(text)
            
            detection = AIDetection.objects.create(
                text=text,
                ai_probability=ai_score * 100,
                is_ai_generated=ai_score > 0.45,
                humanized_text=text
            )
            
            return render(request, 'ai_result.html', {
                'detection': detection,
                'ai_score': ai_score * 100,
                'ai_markers': ai_markers
            })
        except Exception as e:
            messages.error(request, f'Analysis error: {str(e)}')
            return render(request, 'ai_detection.html')
    
    return render(request, 'ai_detection.html')

@login_required
def url_shortener(request):
    if request.method == 'POST':
        original_url = request.POST.get('url', '')
        
        if original_url and URLShortenerService.is_valid_url(original_url):
            short_code = URLShortenerService.generate_short_code()
            
            while URLShortener.objects.filter(short_code=short_code).exists():
                short_code = URLShortenerService.generate_short_code()
            
            url_obj = URLShortener.objects.create(
                original_url=original_url,
                short_code=short_code
            )
            
            messages.success(request, f'Short URL created: {request.build_absolute_uri("/")}{short_code}')
            return render(request, 'url_result.html', {'url_obj': url_obj})
        else:
            messages.error(request, 'Please enter a valid URL')
    
    recent_urls = URLShortener.objects.order_by('-created_at')[:10]
    return render(request, 'url_shortener.html', {'recent_urls': recent_urls})

@login_required
def delete_url(request, url_id):
    url_obj = get_object_or_404(URLShortener, id=url_id)
    url_obj.delete()
    messages.success(request, 'URL deleted successfully')
    return redirect('url_shortener')

def redirect_url(request, short_code):
    url_obj = get_object_or_404(URLShortener, short_code=short_code)
    url_obj.clicks += 1
    url_obj.save()
    return redirect(url_obj.original_url)

@login_required
def qr_generator(request):
    if request.method == 'POST':
        qr_type = request.POST.get('qr_type', 'url')
        content = request.POST.get('content', '')
        
        if qr_type == 'vcard':
            name = request.POST.get('name', '')
            phone = request.POST.get('phone', '')
            email = request.POST.get('email', '')
            organization = request.POST.get('organization', '')
            content = QRCodeGenerator.generate_vcard(name, phone, email, organization)
        elif qr_type == 'portfolio':
            name = request.POST.get('portfolio_name', '')
            url = request.POST.get('portfolio_url', '')
            title = request.POST.get('portfolio_title', '')
            content = f"{name}\n{title}\n{url}"
        elif qr_type == 'certificate':
            cert_name = request.POST.get('cert_name', '')
            cert_id = request.POST.get('cert_id', '')
            cert_url = request.POST.get('cert_url', '')
            content = f"Certificate: {cert_name}\nID: {cert_id}\nVerify: {cert_url}"
        elif qr_type == 'email':
            email_addr = request.POST.get('email_addr', '')
            subject = request.POST.get('email_subject', '')
            content = f"mailto:{email_addr}?subject={subject}" if subject else f"mailto:{email_addr}"
        elif qr_type == 'phone':
            phone_num = request.POST.get('phone_num', '')
            content = f"tel:{phone_num}"
        elif qr_type == 'sms':
            sms_num = request.POST.get('sms_num', '')
            sms_msg = request.POST.get('sms_msg', '')
            content = f"smsto:{sms_num}:{sms_msg}"
        elif qr_type == 'wifi':
            ssid = request.POST.get('wifi_ssid', '')
            password = request.POST.get('wifi_pass', '')
            content = f"WIFI:T:WPA;S:{ssid};P:{password};;"
        elif qr_type == 'event':
            event_name = request.POST.get('event_name', '')
            event_date = request.POST.get('event_date', '')
            event_location = request.POST.get('event_location', '')
            content = f"Event: {event_name}\nDate: {event_date}\nLocation: {event_location}"
        
        if content:
            qr_image = QRCodeGenerator.generate_qr_code(content, qr_type)
            
            qr_obj = QRCode.objects.create(
                qr_type=qr_type,
                content=content,
                image=qr_image
            )
            
            return render(request, 'qr_result.html', {'qr_obj': qr_obj})
    
    recent_qrcodes = QRCode.objects.order_by('-created_at')[:10]
    return render(request, 'qr_generator.html', {'recent_qrcodes': recent_qrcodes})

@login_required
def view_qr(request, qr_id):
    qr_obj = get_object_or_404(QRCode, id=qr_id)
    return render(request, 'qr_detail.html', {'qr_obj': qr_obj})

@login_required
def delete_qr(request, qr_id):
    qr_obj = get_object_or_404(QRCode, id=qr_id)
    qr_obj.delete()
    messages.success(request, 'QR code deleted successfully')
    return redirect('qr_generator')

@login_required
def add_document(request):
    if request.method == 'POST':
        title = request.POST.get('title', '')
        content = request.POST.get('content', '')
        
        if title and content:
            detector = PlagiarismDetector()
            fingerprint = detector.generate_fingerprint(content)
            
            Document.objects.create(
                title=title,
                content=content,
                fingerprint=fingerprint
            )
            
            messages.success(request, 'Document added successfully!')
            return redirect('add_document')
    
    documents = Document.objects.order_by('-created_at')[:10]
    return render(request, 'add_document.html', {'documents': documents})

@login_required
def document_list(request):
    documents = Document.objects.order_by('-created_at')
    return render(request, 'document_list.html', {'documents': documents})

@subscription_required
def plagiarism_removal(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        document = request.FILES.get('document')
        
        if document:
            try:
                text = DocumentParser.extract_text_from_file(document)
            except ValueError as e:
                messages.error(request, f'File Error: {str(e)}')
                return render(request, 'plagiarism_removal.html')
            except Exception as e:
                messages.error(request, f'Unexpected error: {str(e)}')
                return render(request, 'plagiarism_removal.html')
        
        if not text:
            messages.error(request, 'Please provide text or upload a document')
            return render(request, 'plagiarism_removal.html')
        
        try:
            detector = UltimatePlagiarismDetector()
            documents = Document.objects.all()
            
            original_detection = detector.detect_all(text, documents)
            original_plagiarism = original_detection['plagiarism_score'] * 100
            original_ai = original_detection['ai_score'] * 100
            
            remover = PlagiarismRemover()
            result = remover.remove_plagiarism(text, 0.3)
            processed_text = result['processed_text']
            
            humanizer = AIHumanizer()
            humanized_text = humanizer.humanize(processed_text)
            
            new_detection = detector.detect_all(humanized_text, documents)
            new_plagiarism = new_detection['plagiarism_score'] * 100
            new_ai = new_detection['ai_score'] * 100
            
            removal = PlagiarismRemoval.objects.create(
                original_text=text,
                processed_text=humanized_text,
                similarity_before=original_plagiarism,
                similarity_after=new_plagiarism,
                methods_used=result['methods_used']
            )
            
            return render(request, 'plagiarism_removal_result.html', {
                'removal': removal,
                'original_plagiarism': original_plagiarism,
                'new_plagiarism': new_plagiarism,
                'original_ai': original_ai,
                'new_ai': new_ai,
                'plagiarism_improvement': original_plagiarism - new_plagiarism,
                'ai_improvement': original_ai - new_ai,
                'methods_used': result['methods_used']
            })
        except Exception as e:
            messages.error(request, f'Processing error: {str(e)}')
            return render(request, 'plagiarism_removal.html')
    
    return render(request, 'plagiarism_removal.html')

@login_required
def text_summarization(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        document = request.FILES.get('document')
        method = request.POST.get('method', 'extractive')
        summary_length = int(request.POST.get('summary_length', 3))
        
        if document:
            try:
                text = DocumentParser.extract_text_from_file(document)
            except ValueError as e:
                messages.error(request, f'File Error: {str(e)}')
                return render(request, 'text_summarization.html')
            except Exception as e:
                messages.error(request, f'Unexpected error: {str(e)}')
                return render(request, 'text_summarization.html')
        
        if not text:
            messages.error(request, 'Please provide text or upload a document')
            return render(request, 'text_summarization.html')
        
        try:
            service = TextSummarizationService()
            
            if method == 'abstractive':
                summary = service.abstractive_summary(text, max_length=summary_length * 50)
            else:
                summary = service.extractive_summary(text, num_sentences=summary_length)
            
            ratio = len(summary) / len(text) if text else 0
            
            summarization = TextSummarization.objects.create(
                original_text=text,
                summary=summary,
                summary_ratio=ratio,
                method_used=method
            )
            
            return render(request, 'text_summarization_result.html', {
                'summarization': summarization,
                'original_length': len(text),
                'summary_length': len(summary),
                'compression_ratio': (1 - ratio) * 100
            })
        except Exception as e:
            messages.error(request, f'Summarization error: {str(e)}')
            return render(request, 'text_summarization.html')
    
    return render(request, 'text_summarization.html')

@login_required
def sentiment_analysis(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        document = request.FILES.get('document')
        
        if document:
            try:
                text = DocumentParser.extract_text_from_file(document)
            except ValueError as e:
                messages.error(request, f'File Error: {str(e)}')
                return render(request, 'sentiment_analysis.html')
            except Exception as e:
                messages.error(request, f'Unexpected error: {str(e)}')
                return render(request, 'sentiment_analysis.html')
        
        if text:
            service = SentimentAnalysisService()
            result = service.analyze_sentiment(text)
            
            analysis = SentimentAnalysis.objects.create(
                text=text,
                sentiment=result['sentiment'],
                confidence=result['confidence'],
                positive_score=result['positive_score'],
                negative_score=result['negative_score'],
                neutral_score=result['neutral_score']
            )
            
            return render(request, 'sentiment_analysis_result.html', {
                'analysis': analysis,
                'result': result
            })
        else:
            messages.error(request, 'Please enter text or upload a document')
    
    return render(request, 'sentiment_analysis.html')

@login_required
def text_statistics(request):
    if request.method == 'POST':
        text = request.POST.get('text', '').strip()
        document = request.FILES.get('document')
        
        if document:
            try:
                text = DocumentParser.extract_text_from_file(document)
            except ValueError as e:
                messages.error(request, f'File Error: {str(e)}')
                return render(request, 'text_statistics.html')
            except Exception as e:
                messages.error(request, f'Unexpected error: {str(e)}')
                return render(request, 'text_statistics.html')
        
        if text:
            service = TextStatisticsService()
            stats = service.analyze_text(text)
            
            statistics = TextStatistics.objects.create(
                text=text,
                word_count=stats['word_count'],
                character_count=stats['character_count'],
                sentence_count=stats['sentence_count'],
                paragraph_count=stats['paragraph_count'],
                readability_score=stats['readability_score']
            )
            
            return render(request, 'text_statistics_result.html', {
                'statistics': statistics,
                'stats': stats
            })
        else:
            messages.error(request, 'Please enter text or upload a document')
    
    return render(request, 'text_statistics.html')

@login_required
def analytics(request):
    context = {
        'plagiarism_checks': PlagiarismCheck.objects.order_by('-created_at')[:10],
        'ai_detections': AIDetection.objects.order_by('-created_at')[:10],
        'url_stats': URLShortener.objects.order_by('-clicks')[:10],
        'recent_qrcodes': QRCode.objects.order_by('-created_at')[:10],
    }
    return render(request, 'analytics.html', context)

@login_required
def subscription(request):
    try:
        profile = request.user.userprofile
    except UserProfile.DoesNotExist:
        profile = UserProfile.objects.create(user=request.user)
    
    plans = {
        'trial': {'name': 'Trial', 'price': 0, 'duration': '14 days', 'features': ['All 9 services', 'Basic usage limits', 'Email support']},
        'monthly': {'name': 'Monthly', 'price': 2, 'duration': '1 month', 'features': ['All features', 'Unlimited usage', 'Priority support', 'API access']},
        'yearly': {'name': 'Yearly', 'price': 20, 'duration': '1 year', 'features': ['All features', 'Unlimited usage', 'Priority support', 'Save 17%']},
        'unlimited': {'name': 'Unlimited', 'price': 50, 'duration': 'Lifetime', 'features': ['All features forever', 'Unlimited usage', 'VIP support', 'One-time payment']},
    }
    
    return render(request, 'subscription.html', {'profile': profile, 'plans': plans})

@login_required
def upgrade_subscription(request):
    if request.method == 'POST':
        subscription_type = request.POST.get('subscription_type')
        
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        profile.subscription_type = subscription_type
        profile.subscription_start = timezone.now()
        profile.subscription_end = None
        profile.save()
        
        messages.success(request, f'Successfully upgraded to {subscription_type} plan!')
        return redirect('dashboard')
    
    return redirect('subscription')

@login_required
def pdf_converter(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        output_format = request.POST.get('conversion_type', 'pdf')
        
        if file:
            try:
                from .services import DocumentConverter
                file_ext = file.name.split('.')[-1].lower()
                
                if file_ext in ['pdf', 'doc', 'docx', 'txt', 'xls', 'xlsx']:
                    result = DocumentConverter.convert_pdf(file, output_format)
                    return HttpResponse(result['content'], content_type=result['content_type'], headers={'Content-Disposition': f'attachment; filename="{result["filename"]}"'})
                else:
                    messages.error(request, f'Unsupported file format: {file_ext}')
            except Exception as e:
                messages.error(request, f'Conversion error: {str(e)}')
    
    return render(request, 'converters/pdf_converter.html')

@login_required
def word_converter(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        conversion_type = request.POST.get('conversion_type', 'to_docx')
        
        if file:
            try:
                from .services import DocumentConverter
                if conversion_type == 'to_docx':
                    result = DocumentConverter.convert_to_docx(file)
                else:
                    result = DocumentConverter.convert_from_docx(file)
                
                return HttpResponse(result['content'], content_type=result['content_type'], headers={'Content-Disposition': f'attachment; filename="{result["filename"]}"'})
            except Exception as e:
                messages.error(request, f'Conversion error: {str(e)}')
    
    return render(request, 'converters/word_converter.html')

@login_required
def excel_converter(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        conversion_type = request.POST.get('conversion_type', 'to_xlsx')
        
        if file:
            try:
                from .services import DocumentConverter
                if conversion_type == 'to_xlsx':
                    result = DocumentConverter.convert_to_xlsx(file)
                else:
                    result = DocumentConverter.convert_from_xlsx(file)
                
                return HttpResponse(result['content'], content_type=result['content_type'], headers={'Content-Disposition': f'attachment; filename="{result["filename"]}"'})
            except Exception as e:
                messages.error(request, f'Conversion error: {str(e)}')
    
    return render(request, 'converters/excel_converter.html')

@login_required
def image_converter(request):
    if request.method == 'POST':
        file = request.FILES.get('file')
        output_format = request.POST.get('output_format', 'png')
        
        if file:
            try:
                from .services import ImageConverter
                result = ImageConverter.convert_image(file, output_format)
                
                return HttpResponse(result['content'], content_type=result['content_type'], headers={'Content-Disposition': f'attachment; filename="{result["filename"]}"'})
            except Exception as e:
                messages.error(request, f'Conversion error: {str(e)}')
    
    return render(request, 'converters/image_converter.html')

@login_required
def checkout(request, plan=None):
    if not plan:
        return redirect('subscription')
    
    plans_pricing = {
        'trial': 0,
        'monthly': 2,
        'yearly': 20,
        'unlimited': 50,
    }
    
    plan = plan.lower().strip('/')
    
    if plan not in plans_pricing:
        messages.error(request, 'Invalid plan')
        return redirect('subscription')
    
    amount = plans_pricing[plan]
    return render(request, 'checkout.html', {'plan': plan, 'amount': amount})

@login_required
def process_payment(request):
    if request.method == 'POST':
        plan = request.POST.get('plan')
        payment_method = request.POST.get('payment_method', 'card')
        
        plans_pricing = {'trial': 0, 'monthly': 2, 'yearly': 20, 'unlimited': 50}
        
        if plan not in plans_pricing:
            messages.error(request, 'Invalid plan')
            return redirect('subscription')
        
        amount = plans_pricing[plan]
        
        if payment_method == 'card':
            card_number = request.POST.get('card_number', '').replace(' ', '')
            expiry = request.POST.get('expiry', '')
            cvv = request.POST.get('cvv', '')
            
            if not card_number or len(card_number) < 13:
                messages.error(request, 'Invalid card number')
                return redirect('checkout', plan=plan)
            if not expiry or len(expiry) < 5:
                messages.error(request, 'Invalid expiry date')
                return redirect('checkout', plan=plan)
            if not cvv or len(cvv) < 3:
                messages.error(request, 'Invalid CVV')
                return redirect('checkout', plan=plan)
        
        elif payment_method == 'mpesa':
            phone = request.POST.get('phone', '')
            if not phone:
                messages.error(request, 'Phone number required')
                return redirect('checkout', plan=plan)
        
        elif payment_method == 'paypal':
            paypal_email = request.POST.get('paypal_email', '')
            if not paypal_email:
                messages.error(request, 'PayPal email required')
                return redirect('checkout', plan=plan)
        
        import uuid
        transaction_id = str(uuid.uuid4())
        
        from .models import Payment
        payment = Payment.objects.create(
            user=request.user,
            subscription_type=plan,
            amount=amount,
            transaction_id=transaction_id,
            status='completed'
        )
        
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        profile.subscription_type = plan
        profile.subscription_start = timezone.now()
        profile.subscription_end = None
        profile.save()
        
        messages.success(request, f'Payment successful! You are now on the {plan} plan.')
        return redirect('dashboard')
    
    return redirect('subscription')


@login_required
def text_to_speech(request):
    import base64
    from io import BytesIO
    from gtts import gTTS
    from datetime import datetime
    
    voices = {
        'en': ['Professional', 'Conversational', 'Narrator'],
        'es': ['Professional', 'Conversational', 'Narrator'],
        'fr': ['Professional', 'Conversational', 'Narrator'],
        'de': ['Professional', 'Conversational', 'Narrator'],
        'it': ['Professional', 'Conversational', 'Narrator'],
        'pt': ['Professional', 'Conversational', 'Narrator'],
        'ru': ['Professional', 'Conversational', 'Narrator'],
        'ja': ['Professional', 'Conversational', 'Narrator'],
        'zh': ['Professional', 'Conversational', 'Narrator'],
    }
    
    speeches = request.session.get('speeches', [])
    
    if request.method == 'POST':
        delete_index = request.POST.get('delete_index')
        delete_all = request.POST.get('delete_all')
        
        if delete_all:
            request.session['speeches'] = []
            messages.success(request, 'All speeches deleted!')
            return redirect('text_to_speech')
        elif delete_index is not None:
            try:
                idx = int(delete_index)
                if 0 <= idx < len(speeches):
                    speeches.pop(idx)
                    request.session['speeches'] = speeches
                    messages.success(request, 'Speech deleted successfully!')
            except (ValueError, IndexError):
                messages.error(request, 'Error deleting speech')
            return redirect('text_to_speech')
        else:
            text = request.POST.get('text', '').strip()
            language = request.POST.get('language', 'en')
            voice = request.POST.get('voice', 'Professional')
            
            if text:
                try:
                    tts = gTTS(text=text, lang=language, slow=False)
                    audio_buffer = BytesIO()
                    tts.write_to_fp(audio_buffer)
                    audio_buffer.seek(0)
                    audio_data = base64.b64encode(audio_buffer.getvalue()).decode()
                    
                    speech = {
                        'text': text[:100] + '...' if len(text) > 100 else text,
                        'language': language,
                        'voice': voice,
                        'audio': audio_data,
                        'timestamp': datetime.now().strftime('%H:%M:%S')
                    }
                    speeches.insert(0, speech)
                    speeches = speeches[:10]
                    request.session['speeches'] = speeches
                    messages.success(request, 'Speech generated successfully!')
                except Exception as e:
                    messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'text_to_speech.html', {'voices': voices, 'speeches': speeches})

@login_required
def speech_to_text(request):
    if request.method == 'POST':
        audio_file = request.FILES.get('audio')
        
        if audio_file:
            try:
                import speech_recognition as sr
                recognizer = sr.Recognizer()
                with sr.AudioFile(audio_file) as source:
                    audio = recognizer.record(source)
                    text = recognizer.recognize_google(audio)
                
                return render(request, 'speech_to_text_result.html', {'text': text})
            except Exception as e:
                messages.error(request, f'Error: {str(e)}')
    
    return render(request, 'speech_to_text.html')
