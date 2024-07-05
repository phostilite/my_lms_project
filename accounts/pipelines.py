from django.contrib.auth import get_user_model, login
from django.contrib import messages
from django.shortcuts import redirect
from social_core.pipeline.social_auth import social_details, associate_by_email
from social_django.utils import load_strategy
import logging

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
        # This is where you authenticate the user
        # Make sure the user is active or any other checks you want to perform
        if user.is_active:
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            
            if user.groups.filter(name='learner').exists():
                return redirect('learner_dashboard')
            elif user.groups.filter(name='instructor').exists():
                return redirect('instructor_dashboard')
            elif user.groups.filter(name='administrator').exists():
                return redirect('administrator_dashboard')
            else:
                messages.info(request, 'Welcome! Please contact an administrator to assign you a role.')
                return redirect('landing_page')
        else:
            messages.error(request, "Your account is not active. Please contact support.")
            return redirect('login')
        
    except User.DoesNotExist:
        messages.error(request, "User with this email does not exist.")
        return redirect('login')