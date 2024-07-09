from django.contrib.auth import get_user_model, login
from django.shortcuts import redirect
from social_core.pipeline.partial import partial
import logging
from django.contrib.auth.models import Group
from .models import Learner
from django.db import IntegrityError, transaction
from .utils import redirect_based_on_group

logger = logging.getLogger(__name__)

User = get_user_model()

@partial
def handle_auth_flow(backend, details, response, *args, **kwargs):
    """
    Handle both sign-in and sign-up flows for Google authentication.
    """
    print("Handling auth flow")
    print(f"Backend: {backend}")
    print(f"Details: {details}")
    print(f"Response: {response}")
    print(f"Args: {args}")
    print(f"Kwargs: {kwargs}")

    # Ensure session data is cleared
    request = backend.strategy.request
    request.session.flush()

    # Log the entire response to check the email being sent by Google
    logger.debug(f"OAuth response: {response}")

    email = details.get('email')
    first_name = details.get('first_name', '')
    last_name = details.get('last_name', '')

    if not email:
        error_messages = ["Email not found in your Google account."]
        request.session['error_messages'] = error_messages
        return redirect('login')

    # Determine if the user exists to decide the auth_flow
    user_exists = User.objects.filter(email=email).exists()
    auth_flow = 'signin' 
    print(f"Auth flow: {auth_flow}")

    error_messages = []

    if auth_flow == 'signin':
        if user_exists:
            user = User.objects.get(email=email)
            if user.is_active:
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect_based_on_group(request, user)
            else:
                error_messages.append("Your account is not active. Please contact support.")
        else:
            error_messages.append("No account found with this email. Please sign up first.")
            request.session['auth_flow'] = 'signin'
            request.session['error_messages'] = error_messages
            return redirect('login')

    elif auth_flow == 'signup':
        if user_exists:
            error_messages.append("An account with this email already exists. Please login.")
            request.session['error_messages'] = error_messages
            return redirect('login')
        else:
            try:
                with transaction.atomic():
                    user = User.objects.create_user(
                        username=email, email=email, first_name=first_name, last_name=last_name
                    )
                    user.is_active = True
                    user.save()

                    group, _ = Group.objects.get_or_create(name='learner')
                    user.groups.add(group)

                    Learner.objects.create(user=user)

                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    return redirect_based_on_group(request, user)
            except IntegrityError:
                error_messages.append("There was a problem creating your account. Please try again.")
                request.session['error_messages'] = error_messages
                return redirect('signup')
            except Exception as e:
                error_messages.append(f"Unexpected error: {str(e)}")
                request.session['error_messages'] = error_messages
                return redirect('signup')

    return None
