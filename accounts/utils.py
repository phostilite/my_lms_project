from django.shortcuts import redirect
from django.contrib import messages

from msal import ConfidentialClientApplication
from django.conf import settings

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
        
def get_msal_app():
    return ConfidentialClientApplication(
        client_id=settings.SOCIAL_AUTH_MICROSOFT_OAUTH2_KEY,
        client_credential=settings.SOCIAL_AUTH_MICROSOFT_OAUTH2_SECRET,
        authority=f"https://login.microsoftonline.com/{settings.SOCIAL_AUTH_MICROSOFT_OAUTH2_TENANT_ID}",
    )