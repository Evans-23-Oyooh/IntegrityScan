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
