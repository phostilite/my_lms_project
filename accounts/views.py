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
from django.contrib.auth.models import Group
from django.db import transaction
from django.db.utils import IntegrityError
from django.views.decorators.debug import sensitive_post_parameters
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.cache import never_cache
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.utils.translation import gettext as _


from .forms import LoginForm, LearnerSignupForm
from .utils import redirect_based_on_group, get_msal_app
from .auth_helper import get_sign_in_flow, get_token_from_code, store_user, get_token, remove_user_and_token, extract_user_details
from .graph_helper import *
from .models import Learner

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
            return redirect('admin_dashboard')
        elif user.groups.filter(name='instructor').exists():
            return redirect('instructor_dashboard')
        else:
            return redirect('learner_dashboard')


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