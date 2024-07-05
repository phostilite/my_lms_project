from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.shortcuts import redirect
from social_core.pipeline.social_auth import social_details, associate_by_email
from social_django.utils import load_strategy
import logging

from .utils import redirect_based_on_group

logger = logging.getLogger(__name__)

User = get_user_model()

def social_auth_user(backend, details, response, *args, **kwargs):
    """Pipeline function to handle social authentication."""
    request = backend.strategy.request
    email = details.get('email')
    if not email:
        messages.error(request, "Email not found in your Google account.")
        return redirect('login')
    try:
        user = User.objects.get(email=email)
        if user.is_active:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect_based_on_group(request, user)
        else:
            messages.error(request, "Your account is not active. Please contact support.")
            return redirect('login')
        
    except User.DoesNotExist:
        messages.error(request, "User with this email does not exist.")
        return redirect('login')