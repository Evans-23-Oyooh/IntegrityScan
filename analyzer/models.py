from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid

class UserProfile(models.Model):
    SUBSCRIPTION_CHOICES = [
        ('trial', 'Trial (14 days)'),
        ('monthly', 'Monthly ($2/month)'),
        ('yearly', 'Yearly ($20/year)'),
        ('unlimited', 'Unlimited ($50 one-time)'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=20, choices=SUBSCRIPTION_CHOICES, default='trial')
    subscription_start = models.DateTimeField(default=timezone.now)
    subscription_end = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.subscription_end:
            if self.subscription_type == 'trial':
                self.subscription_end = self.subscription_start + timedelta(days=14)
            elif self.subscription_type == 'monthly':
                self.subscription_end = self.subscription_start + timedelta(days=30)
            elif self.subscription_type == 'yearly':
                self.subscription_end = self.subscription_start + timedelta(days=365)
            elif self.subscription_type == 'unlimited':
                self.subscription_end = None
        super().save(*args, **kwargs)
    
    @property
    def is_subscription_active(self):
        if self.subscription_type == 'unlimited':
            return True
        return self.subscription_end and timezone.now() < self.subscription_end
    
    @property
    def days_remaining(self):
        if self.subscription_type == 'unlimited':
            return float('inf')
        if self.subscription_end:
            remaining = self.subscription_end - timezone.now()
            return max(0, remaining.days)
        return 0

class Document(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    content = models.TextField()
    fingerprint = models.CharField(max_length=64)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class PlagiarismCheck(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    similarity_score = models.FloatField()
    is_plagiarized = models.BooleanField(default=False)
    matches = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

class AIDetection(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    ai_probability = models.FloatField()
    is_ai_generated = models.BooleanField(default=False)
    humanized_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class URLShortener(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_url = models.URLField(max_length=2000)
    short_code = models.CharField(max_length=10, unique=True)
    clicks = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.short_code} -> {self.original_url}"

class TextSummarization(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_text = models.TextField()
    summary = models.TextField()
    summary_ratio = models.FloatField()
    method_used = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class LanguageTranslation(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_text = models.TextField()
    translated_text = models.TextField()
    source_language = models.CharField(max_length=10)
    target_language = models.CharField(max_length=10)
    created_at = models.DateTimeField(auto_now_add=True)

class SentimentAnalysis(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    sentiment = models.CharField(max_length=20)
    confidence = models.FloatField()
    positive_score = models.FloatField()
    negative_score = models.FloatField()
    neutral_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class KeywordExtraction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    keywords = models.JSONField(default=list)
    method_used = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)

class TextStatistics(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    text = models.TextField()
    word_count = models.IntegerField()
    character_count = models.IntegerField()
    sentence_count = models.IntegerField()
    paragraph_count = models.IntegerField()
    readability_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

class PlagiarismRemoval(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    original_text = models.TextField()
    processed_text = models.TextField()
    similarity_before = models.FloatField()
    similarity_after = models.FloatField()
    methods_used = models.JSONField(default=list)
    created_at = models.DateTimeField(auto_now_add=True)

class QRCode(models.Model):
    TYPES = [
        ('url', 'URL'),
        ('text', 'Text'),
        ('vcard', 'vCard'),
        ('wifi', 'WiFi'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    qr_type = models.CharField(max_length=10, choices=TYPES, default='url')
    content = models.TextField()
    image = models.ImageField(upload_to='qrcodes/')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.qr_type} - {self.content[:50]}"

class EmailVerification(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    verification_code = models.CharField(max_length=6, unique=True)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def is_expired(self):
        return timezone.now() > self.expires_at

class PasswordReset(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reset_code = models.CharField(max_length=6, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    
    def is_expired(self):
        return timezone.now() > self.expires_at

class Payment(models.Model):
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subscription_type = models.CharField(max_length=20)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_method = models.CharField(max_length=50, default='card')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} - {self.subscription_type} - {self.status}"