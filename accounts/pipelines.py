from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from social_core.pipeline.partial import partial
import logging

from .utils import redirect_based_on_group

logger = logging.getLogger(__name__)

User = get_user_model()

@partial
def check_user_exists(backend, details, response, *args, **kwargs):
    """
    Check if a user with the given email exists and handle accordingly.
    """
    request = backend.strategy.request
    email = details.get('email')

    error_messages = []

    if not email:
        error_messages.append("Email not found in your Google account.")
    else:
        try:
            user = User.objects.get(email=email)
            if user.is_active:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect_based_on_group(request, user)
            else:
                error_messages.append("Your account is not active. Please contact support.")
        except User.DoesNotExist:
            error_messages.append("No account found with this email. Please sign up first.")

    if error_messages:
        # Store error messages in the session
        request.session['error_messages'] = error_messages
        return redirect('login')

def social_auth_user(*args, **kwargs):
    """
    This function will not be called if check_user_exists redirects,
    effectively preventing new user creation.
    """
    return None