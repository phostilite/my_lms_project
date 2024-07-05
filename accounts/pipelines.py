from social_core.pipeline.social_auth import social_details, associate_by_email
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.shortcuts import redirect
import logging

from .utils import redirect_based_on_group

logger = logging.getLogger(__name__)

User = get_user_model()

def social_auth_user(backend, details, response, *args, **kwargs):
    """Pipeline function to handle social authentication."""
    logger.info(f"Social auth response: {response}")
    logger.info(f"Social auth details: {details}")
    logger.info(f"Social auth backend: {backend}")

    print("Social auth response: ", response)
    print("Social auth details: ", details)
    print("Social auth backend: ", backend)
    
    email = details.get('email')
    if not email:
        messages.error(backend.strategy.request, "Email not found in your Google account.")
        return redirect('login')
    try:
        user = User.objects.get(email=email)
        logger.info(f"User with email {email} already exists.")
    except User.DoesNotExist:
        messages.error(backend.strategy.request, "User with this email does not exist.")
        logger.warning(f"User with email {email} does not exist.")
        return redirect('login')  # Or handle the error differently

    # Associate the social account with the existing user
    associate_by_email(backend, details, *args, **kwargs)  

    # Use the redirect_based_on_group function for redirection
    return redirect_based_on_group(backend.strategy.request, user)