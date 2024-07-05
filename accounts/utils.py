from django.shortcuts import redirect
from django.contrib import messages


def redirect_based_on_group(request, user):
        if user.groups.filter(name='learner').exists():
            return redirect('learner_dashboard')
        elif user.groups.filter(name='instructor').exists():
            return redirect('instructor_dashboard')
        elif user.groups.filter(name='administrator').exists():
            return redirect('administrator_dashboard')
        else:
            messages.info(request, 'Welcome! Please contact an administrator to assign you a role.')
            return redirect('landing_page')