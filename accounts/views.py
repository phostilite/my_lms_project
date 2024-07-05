from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.contrib import messages
from social_django.models import UserSocialAuth
from django.contrib.auth import authenticate, login, logout, get_user_model
import logging
import uuid
from msal import ConfidentialClientApplication
from django.conf import settings
import requests
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from .forms import LoginForm, LearnerSignupForm
from .utils import redirect_based_on_group, get_msal_app
from .auth_helper import get_sign_in_flow, get_token_from_code, store_user, get_token, remove_user_and_token, extract_user_details
from .graph_helper import *

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

class LoginView(LoginView):
    template_name = 'authentication/login.html'
    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """Security check complete. Log the user in and redirect based on role."""
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(self.request, username=username, password=password)

        if user is not None:
            login(self.request, user)
            logger.info(f"User {username} logged in successfully.")
            return redirect_based_on_group(self.request, user)  

        else:
            messages.error(self.request, 'Invalid username or password.')
            logger.warning(f"Failed login attempt for username: {username}")

        return super().form_invalid(form)  
    
    def form_invalid(self, form):
        logger.error(f"Form invalid: {form.errors}")
        messages.error(self.request, "There were errors in your form submission.")
        return super().form_invalid(form)


class LearnerSignupView(LoginView):
    template_name = 'authentication/signup.html'
    form_class = LearnerSignupForm

    def post(self, request, *args, **kwargs):
        form = self.get_form()
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        """Create a new user and log them in."""
        try:
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            username = form.cleaned_data.get('username')
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')

            # Create a new user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.first_name = first_name
            user.last_name = last_name
            user.save()

            # Log the user in
            login(self.request, user)
            messages.success(self.request, 'Account created successfully!')
            return redirect('learner_dashboard')
        except Exception as e:
            logger.error(f"Error creating user: {e}")
            messages.error(self.request, 'There was an error creating your account. Please try again.')
            return self.form_invalid(form)


def user_logout(request):
    logout(request)
    return redirect('login')


def initialize_context(request):
    context = {}
    error = request.session.pop('flash_error', None)
    if error is not None:
        context['errors'] = [error]
    context['user'] = request.session.get('user', {'is_authenticated': False})
    return context

def microsoft_sign_in(request):
    # Get the sign-in flow
    flow = get_sign_in_flow()
    # Save the expected flow so we can use it in the callback
    try:
        request.session['auth_flow'] = flow
    except Exception as e:
        print(e)    
    return HttpResponseRedirect(flow['auth_uri'])

def microsoft_sign_out(request):
    # Clear out the user and token
    remove_user_and_token(request)
    return HttpResponseRedirect(reverse('landing_page'))

# In your callback function:
def callback(request):
    # Make the token request
    result = get_token_from_code(request)
    if 'error' in result:
        messages.error(request, 'There was an error logging you in with Microsoft. Please try again.')
        return redirect('login')

    # Extract user details
    user_info = extract_user_details(result)
    print(f"user_info: {user_info}")

    # Store user information in session
    store_user(request, user_info)

    # Try to find the user by email
    try:
        email = user_info.get('email')
        if not email:
            raise KeyError("Email not found in user info")
        
        user = User.objects.get(email=email)
    except (User.DoesNotExist, KeyError) as e:
        if isinstance(e, KeyError):
            messages.error(request, 'Unable to retrieve email from Microsoft. Please try again or contact support.')
        else:
            messages.error(request, 'No account found for the given email. Please contact support or try a different login method.')
        return redirect('login')

    # If the user exists, log them in
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')

    # Redirect the user based on their group
    return redirect_based_on_group(request, user)