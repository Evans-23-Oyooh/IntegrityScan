from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile

def subscription_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            profile = request.user.userprofile
        except UserProfile.DoesNotExist:
            profile = UserProfile.objects.create(user=request.user)
        
        if not profile.is_subscription_active:
            messages.error(request, 'Your subscription has expired. Please upgrade to continue using our services.')
            return redirect('subscription')
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view