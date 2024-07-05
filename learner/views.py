import logging
from django.shortcuts import render
from django.http import HttpResponseServerError
from django.http import Http404
from django.contrib.auth.decorators import login_required

from courses.models import ScormCloudCourse, ScormCloudRegistration
from accounts.models import Learner


# Configure the logger
logger = logging.getLogger(__name__)

@login_required
def dashboard(request):
    try:
        return render(request, 'learner/dashboard.html')
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return HttpResponseServerError("An error occurred")

@login_required    
def progress(request):
    return render(request, 'learner/progress.html')

@login_required
def calendar(request):
    try:
        return render(request, 'learner/calendar.html')
    except Exception as e:
        logger.error(f"Error loading calendar: {e}")
        return HttpResponseServerError("An error occurred")

@login_required
def course_catalog(request):
    try:
        courses = ScormCloudCourse.objects.all()
    except ScormCloudCourse.DoesNotExist:
        courses = None
    except Exception as e:
        logger.error(f"Error loading course catalog: {e}")
        courses = None
    return render(request, 'learner/course_catalog.html', {'courses': courses})

@login_required
def courses(request):
    try:
        # Fetch registrations for the logged-in learner
        registrations = ScormCloudRegistration.objects.filter(learner=request.user.learner)

        # Prepare course data for the template
        course_data = []
        for registration in registrations:
            try:
                course = ScormCloudCourse.objects.get(course_id=registration.course_id)
                course_data.append({
                    'registration': registration,
                    'course': course
                })
            except ScormCloudCourse.DoesNotExist:
                logger.warning(f"Course with ID '{registration.course_id}' not found for registration {registration.registration_id}.")
                # Handle the case where the course doesn't exist
                # Option 1: Skip and don't show the registration
                # Option 2: Show an error message in the template

        return render(request, 'learner/courses.html', {'course_data': course_data})

    except Learner.DoesNotExist:  # If the learner object does not exist (i.e., the user is not a learner)
        raise Http404("Learner profile not found.") 
    except Exception as e:  # Catch-all for other unexpected errors
        logger.error(f"Unexpected error loading courses: {e}")
        return HttpResponseServerError("An error occurred while loading courses.")

@login_required
def certificates(request):
    try:
        return render(request, 'learner/certificates.html')
    except Exception as e:
        logger.error(f"Error loading certificates: {e}")
        return HttpResponseServerError("An error occurred")

@login_required
def badge(request):
    try:
        return render(request, 'learner/badge.html')
    except Exception as e:
        logger.error(f"Error loading badge: {e}")
        return HttpResponseServerError("An error occurred")

@login_required    
def leaderboard(request):
    try:
        return render(request, 'learner/leaderboard.html')
    except Exception as e:
        logger.error(f"Error loading leaderboard: {e}")
        return HttpResponseServerError("An error occurred")