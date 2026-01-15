from django.contrib import admin
from .models import Document, PlagiarismCheck, AIDetection, URLShortener, QRCode, PlagiarismRemoval

@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['title', 'fingerprint', 'created_at']
    search_fields = ['title', 'content']
    readonly_fields = ['fingerprint', 'created_at', 'updated_at']

@admin.register(PlagiarismCheck)
class PlagiarismCheckAdmin(admin.ModelAdmin):
    list_display = ['similarity_score', 'is_plagiarized', 'created_at']
    list_filter = ['is_plagiarized', 'created_at']
    readonly_fields = ['created_at']

@admin.register(AIDetection)
class AIDetectionAdmin(admin.ModelAdmin):
    list_display = ['ai_probability', 'is_ai_generated', 'created_at']
    list_filter = ['is_ai_generated', 'created_at']
    readonly_fields = ['created_at']

@admin.register(URLShortener)
class URLShortenerAdmin(admin.ModelAdmin):
    list_display = ['short_code', 'original_url', 'clicks', 'created_at']
    search_fields = ['short_code', 'original_url']
    readonly_fields = ['created_at']

@admin.register(PlagiarismRemoval)
class PlagiarismRemovalAdmin(admin.ModelAdmin):
    list_display = ['similarity_before', 'similarity_after', 'created_at']
    list_filter = ['created_at']
    readonly_fields = ['created_at']

@admin.register(QRCode)
class QRCodeAdmin(admin.ModelAdmin):
    list_display = ['qr_type', 'content', 'created_at']
    list_filter = ['qr_type', 'created_at']
    readonly_fields = ['created_at']