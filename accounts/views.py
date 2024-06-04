from django.contrib.auth.views import LoginView
from django.shortcuts import redirect, render
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout

from .forms import CustomLoginForm

def landing_page(request):
    return render(request, 'landing_page.html')

class CustomLoginView(LoginView):
    template_name = 'authentication/login.html'
    form_class = CustomLoginForm

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

            if user.groups.filter(name='learner').exists():
                messages.success(self.request, 'Welcome, Learner!')
                return redirect('learner_dashboard')  
            elif user.groups.filter(name='instructor').exists():
                messages.success(self.request, 'Welcome, Instructor!')
                return redirect('instructor_dashboard')
            elif user.groups.filter(name='administrator').exists():
                messages.success(self.request, 'Welcome, Administrator!')
                return redirect('admin_dashboard')
        else:
            messages.error(self.request, 'Invalid username or password.')

        return super().form_invalid(form)

def user_logout(request):
    logout(request)
    return redirect('login')  