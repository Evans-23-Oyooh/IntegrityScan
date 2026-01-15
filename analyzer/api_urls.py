from django.urls import path
from . import api_views

urlpatterns = [
    path('plagiarism-check/', api_views.plagiarism_check_api, name='api_plagiarism_check'),
    path('plagiarism-removal/', api_views.plagiarism_removal_api, name='api_plagiarism_removal'),
    path('ai-detection/', api_views.ai_detection_api, name='api_ai_detection'),
    path('shorten-url/', api_views.shorten_url_api, name='api_shorten_url'),
    path('generate-qr/', api_views.generate_qr_api, name='api_generate_qr'),
    path('add-document/', api_views.add_document_api, name='api_add_document'),
]