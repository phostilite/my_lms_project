# Standard library imports
import logging
import uuid
from urllib.parse import urlencode

# Third-party imports
import requests
from msal import ConfidentialClientApplication
from social_django.models import UserSocialAuth

# Django imports
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.models import Group
from django.contrib.auth.views import LoginView, LoginView as DjangoLoginView, PasswordResetView
from django.contrib.messages.views import SuccessMessageMixin
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db import transaction
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils.decorators import method_decorator
from django.utils.translation import gettext as _
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.debug import sensitive_post_parameters

# Local application/library specific imports
from . import constants
from .auth_helper import extract_user_details, get_sign_in_flow, get_token, get_token_from_code, remove_user_and_token, store_user
from .backends import GoogleSignInBackend
from .forms import LoginForm, LearnerSignupForm
from .graph_helper import *
from .models import Learner
from .utils import get_msal_app, redirect_based_on_group

logger = logging.getLogger(__name__)

User = get_user_model()


def landing_page(request):
    context = initialize_context(request)
    return render(request, 'landing_page.html', context)

def about(request):
    return render(request, 'about.html')

def contact(request):
    return render(request, 'contact.html')

def courses(request):
    return render(request, 'courses.html')

def privacy_policy(request):
    return render(request, 'privacy_policy.html')


# Django Authentication
class LoginView(DjangoLoginView):
    template_name = 'authentication/login.html'
    form_class = LoginForm

    @method_decorator(sensitive_post_parameters())
    @method_decorator(csrf_protect)
    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return self.redirect_authenticated_user(self.request.user)
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        """Security check complete. Log the user in and redirect based on role."""
        login(self.request, form.get_user())
        logger.info(f"User {form.get_user().username} logged in successfully.")
        messages.success(self.request, _('You have successfully logged in.'))
        return self.redirect_authenticated_user(form.get_user())

    def form_invalid(self, form):
        logger.warning(f"Failed login attempt for username: {form.data.get('username')}")
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    error_messages.append(str(error))
                else:
                    error_messages.append(f"{field.capitalize()}: {error}")
        
        messages.error(self.request, _('Login failed. Please check the errors below.'))
        return self.render_to_response(self.get_context_data(form=form, error_messages=error_messages))


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['request'] = self.request
        return kwargs

    def redirect_authenticated_user(self, user):
        """Redirect users based on their group."""
        if user.groups.filter(name='administrator').exists():
            return redirect('administrator_dashboard')
        elif user.groups.filter(name='instructor').exists():
            return redirect('instructor_dashboard')
        else:
            return redirect('learner_dashboard')
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Get error messages from session (set by Google sign-in pipeline)
        google_error_messages = self.request.session.pop('error_messages', None)
        if google_error_messages:
            context['error_messages'] = google_error_messages
        return context


class LearnerSignupView(LoginView):
    template_name = 'authentication/signup.html'
    form_class = LearnerSignupForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs.pop('request', None)  
        return kwargs

    @transaction.atomic
    def form_valid(self, form):
        try:
            user = form.save()
            group, _ = Group.objects.get_or_create(name='learner')
            user.groups.add(group)
            Learner.objects.create(user=user)
            messages.success(self.request, 'Account created successfully!')
            return self.login_and_redirect(user)
        except IntegrityError as e:
            logger.error(f"IntegrityError creating user: {e}")
            messages.error(self.request, 'An account with this email already exists.')
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            messages.error(self.request, 'There was an error creating your account. Please try again.')
        return self.form_invalid(form)

    def login_and_redirect(self, user):
        from django.contrib.auth import login
        login(self.request, user, backend='django.contrib.auth.backends.ModelBackend')
        return redirect('learner_dashboard')  

    def form_invalid(self, form):
        logger.warning(f"Failed signup attempt with data: {form.data}")
        error_messages = []
        for field, errors in form.errors.items():
            for error in errors:
                if field == '__all__':
                    error_messages.append(str(error))
                else:
                    error_messages.append(f"{field.capitalize()}: {error}")

        messages.error(self.request, _('Signup failed. Please check the errors below.'))
        return self.render_to_response(self.get_context_data(form=form, error_messages=error_messages))
    
def user_logout(request):
    remove_user_and_token(request)
    logout(request)
    return redirect('login')


# Microsoft OAuth2

def initialize_context(request):
    context = {}
    error = request.session.pop('flash_error', None)
    if error is not None:
        context['errors'] = [error]
    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context

def microsoft_sign_in(request):
    flow = get_sign_in_flow()

    request.session['auth_action'] = 'sign_in'

    # Save the flow and redirect
    request.session['auth_flow'] = flow
    return HttpResponseRedirect(flow['auth_uri'])

def microsoft_sign_up(request):
    flow = get_sign_in_flow()

    request.session['auth_action'] = 'sign_up'

    # Save the flow and redirect
    request.session['auth_flow'] = flow
    return HttpResponseRedirect(flow['auth_uri'])

@transaction.atomic
def microsoft_callback(request):
    # Retrieve the auth action from the session
    auth_action = request.session.pop('auth_action', None) 

    if auth_action == 'sign_in':
        # Call your sign-in callback logic
        return microsoft_sign_in_callback(request)
    elif auth_action == 'sign_up':
        # Call your sign-up callback logic
        return microsoft_sign_up_callback(request)
    else:
        # Handle invalid or missing auth action
        logger.error("Invalid or missing auth_action in Microsoft callback")
        return redirect('login')  # Or an appropriate error page

@transaction.atomic
def microsoft_sign_in_callback(request):
    try:
        result = get_token_from_code(request)
        if 'error' in result:
            raise Exception(result.get('error_description', 'Unknown error occurred'))

        user_info = extract_user_details(result)
        email = user_info.get('email')
        
        if not email:
            raise KeyError("Email not found in user info")

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                raise Exception("Your account is not active. Please contact support.")
            
            # Log the user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            logger.info(f"User {user.username} logged in successfully via Microsoft.")
            return redirect_based_on_group(request, user)

        except User.DoesNotExist:
            # User doesn't exist, set error message and redirect to login page
            error_message = "No account found with this email. Please sign up first."
            request.session['error_messages'] = [error_message]
            logger.warning(f"Failed login attempt via Microsoft for email: {email}")
            return redirect('login')

    except KeyError as e:
        logger.error(f"KeyError in Microsoft callback: {e}")
        error_message = 'Unable to retrieve email from Microsoft. Please try again or contact support.'
    except Exception as e:
        logger.error(f"Error in Microsoft callback: {e}")
        error_message = str(e)
    
    request.session['error_messages'] = [error_message]
    return redirect('login')


@transaction.atomic
def microsoft_sign_up_callback(request):
    try:
        result = get_token_from_code(request)
        if 'error' in result:
            raise Exception(result.get('error_description', 'Unknown error occurred'))

        user_info = extract_user_details(result)
        email = user_info.get('email')
        full_name = user_info.get('name')

        if not email:
            raise KeyError("Email not found in user info")
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            error_message = "An account with this email already exists. Please sign in instead."
            request.session['error_messages'] = [error_message]
            logger.warning(f"Failed signup attempt via Microsoft (email already exists): {email}")
            return redirect('login')

        if full_name:
            first_name, last_name = full_name.split(' ', 1)
        else:
            first_name, last_name = "", ""

        # Create new user
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=first_name,
            last_name=last_name,
        )
        user.is_active = True
        user.save()
        group, _ = Group.objects.get_or_create(name='learner')
        user.groups.add(group)
        Learner.objects.create(user=user)

        logger.info(f"New user {user.username} created via Microsoft.")
        
        # Optionally send welcome/verification email

        login(request, user, backend='django.contrib.auth.backends.ModelBackend')  # Log them in immediately
        return redirect('set_password')

    except KeyError as e:
        logger.error(f"KeyError in Microsoft sign-up callback: {e}")
        error_message = 'Unable to retrieve email from Microsoft. Please try again or contact support.'
    except Exception as e:
        logger.error(f"Error in Microsoft sign-up callback: {e}")
        error_message = str(e)

    request.session['error_messages'] = [error_message]
    return redirect('login')


def google_auth(request):
    return HttpResponseRedirect(constants.GOOGLE_LOGIN_REDIRECT_URI)


def google_auth_callback(request):
    print(f'Google Callback: {request.GET}')
    error_messages = []

    flow = 'signin'

    if flow == 'signin':
        if 'error' in request.GET:
            error_messages.append("Google authentication failed. Please try again.")
            request.session['error_messages'] = error_messages
            return redirect('login')

        if 'code' in request.GET:
            user = authenticate(request, code=request.GET.get('code'), backend='accounts.backends.GoogleSignInBackend')
            if user:
                login(request, user=user)
                return redirect_based_on_group(request, user)
            else:
                error_messages.append("No account found with this email. Please sign up first.")
                request.session['error_messages'] = error_messages
                return redirect('login')

        error_messages.append("Invalid request. Please try again.")
        request.session['error_messages'] = error_messages
        return redirect('login')
    else:
        error_messages.append("Invalid flow. Please try again.")
        request.session['error_messages'] = error_messages
        return redirect('login')
    


class ResetPasswordView(SuccessMessageMixin, PasswordResetView):
    template_name = 'resets/password_reset_form.html'
    email_template_name = 'resets/password_reset_email.html'
    subject_template_name = 'resets/password_reset_subject.txt'
    success_message = "We've emailed you instructions for setting your password, " \
                      "if an account exists with the email you entered. You should receive them shortly." \
                      " If you don't receive an email, " \
                      "please make sure you've entered the address you registered with, and check your spam folder."
    success_url = reverse_lazy('landing_page')


