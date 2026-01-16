from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import random
import string
from .models import EmailVerification, PasswordReset

def welcome(request):
    return render(request, 'index.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            
            # Generate verification code
            verification_code = ''.join(random.choices(string.digits, k=6))
            expires_at = timezone.now() + timedelta(hours=24)
            
            EmailVerification.objects.create(
                user=user,
                verification_code=verification_code,
                expires_at=expires_at
            )
            
            # Send email
            send_mail(
                'Verify Your Email - IntegrityScan',
                f'Your verification code is: {verification_code}\n\nThis code expires in 24 hours.',
                settings.DEFAULT_FROM_EMAIL,
                [user.email or user.username + '@example.com'],
                fail_silently=False,
            )
            
            messages.success(request, 'Account created! Check your email for verification code.')
            return redirect('verify_email', username=user.username)
    else:
        form = UserCreationForm()
    return render(request, 'auth/register.html', {'form': form})

def verify_email(request, username):
    try:
        user = User.objects.get(username=username)
        verification = EmailVerification.objects.get(user=user)
    except (User.DoesNotExist, EmailVerification.DoesNotExist):
        messages.error(request, 'Invalid verification request')
        return redirect('register')
    
    if verification.is_verified:
        messages.info(request, 'Email already verified. Please login.')
        return redirect('login')
    
    if request.method == 'POST':
        code = request.POST.get('code', '')
        
        if verification.is_expired():
            messages.error(request, 'Verification code expired. Please register again.')
            user.delete()
            return redirect('register')
        
        if code == verification.verification_code:
            verification.is_verified = True
            verification.save()
            user.is_active = True
            user.save()
            messages.success(request, 'Email verified! You can now login.')
            return redirect('login')
        else:
            messages.error(request, 'Invalid verification code')
    
    return render(request, 'auth/verify_email.html', {'username': username, 'verification_code': verification.verification_code})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'auth/login.html')

def logout_view(request):
    logout(request)
    return redirect('welcome')

@login_required
def about_view(request):
    return render(request, 'about.html')

@login_required
def contact_view(request):
    return render(request, 'contact.html')

@login_required
def blog_view(request):
    return render(request, 'blog.html')

@login_required
def careers_view(request):
    return render(request, 'careers.html')

def privacy_view(request):
    return render(request, 'privacy_policy.html')

def terms_view(request):
    return render(request, 'terms_of_service.html')

def cookies_view(request):
    return render(request, 'cookie_policy.html')

def gdpr_view(request):
    return render(request, 'gdpr.html')

def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email', '')
        try:
            user = User.objects.get(email=email)
            # Delete old reset codes
            PasswordReset.objects.filter(user=user, is_used=False).delete()
            
            # Generate reset code
            reset_code = ''.join(random.choices(string.digits, k=6))
            expires_at = timezone.now() + timedelta(hours=24)
            
            PasswordReset.objects.create(
                user=user,
                reset_code=reset_code,
                expires_at=expires_at
            )
            
            # Send email
            send_mail(
                'Password Reset Code - IntegrityScan',
                f'Your password reset code is: {reset_code}\n\nThis code expires in 24 hours.\n\nIf you did not request this, please ignore this email.',
                settings.DEFAULT_FROM_EMAIL,
                [email],
                fail_silently=False,
            )
            
            messages.success(request, 'Reset code sent to your email. Check your inbox.')
            return redirect('reset_password')
        except User.DoesNotExist:
            messages.error(request, 'No account found with this email.')
    
    return render(request, 'auth/forgot_password.html')

def reset_password(request):
    if request.method == 'POST':
        reset_code = request.POST.get('reset_code', '')
        new_password = request.POST.get('new_password', '')
        confirm_password = request.POST.get('confirm_password', '')
        
        if new_password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'auth/reset_password.html')
        
        try:
            reset = PasswordReset.objects.get(reset_code=reset_code, is_used=False)
            
            if reset.is_expired():
                messages.error(request, 'Reset code expired. Please request a new one.')
                return redirect('forgot_password')
            
            # Update password
            user = reset.user
            user.set_password(new_password)
            user.save()
            
            # Mark as used
            reset.is_used = True
            reset.save()
            
            messages.success(request, 'Password reset successfully. You can now login.')
            return redirect('login')
        except PasswordReset.DoesNotExist:
            messages.error(request, 'Invalid reset code.')
    
    return render(request, 'auth/reset_password.html')

def google_oauth(request):
    return redirect('https://accounts.google.com/o/oauth2/v2/auth?client_id=YOUR_GOOGLE_CLIENT_ID&redirect_uri=http://localhost:8000/auth/google/callback&response_type=code&scope=openid%20email%20profile')