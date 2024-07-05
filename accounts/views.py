from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.contrib import messages
from social_django.models import UserSocialAuth
from django.contrib.auth import authenticate, login, logout, get_user_model
import logging

from .forms import LoginForm, LearnerSignupForm
from .utils import redirect_based_on_group

logger = logging.getLogger(__name__)

User = get_user_model()


def landing_page(request):
    return render(request, 'landing_page.html')

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
