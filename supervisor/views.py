from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import logging
from django.http import HttpResponseServerError

logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    try:
        return render(request, 'supervisor/dashboard.html')
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return HttpResponseServerError("An error occurred")
