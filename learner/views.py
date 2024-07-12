import logging
from django.shortcuts import render, redirect
from django.http import HttpResponseServerError
from django.http import Http404
from django.contrib.auth.decorators import login_required
import pytz
from datetime import datetime

from courses.models import ScormCloudCourse, ScormCloudRegistration, CourseDelivery
from accounts.models import Learner
from accounts.forms import UserTimeZoneForm


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
    
@login_required
def settings(request):
    try:
        if request.method == 'POST':
            form = UserTimeZoneForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                return redirect('learner_settings')
        else:
            form = UserTimeZoneForm(instance=request.user)
        return render(request, 'learner/settings.html', {'form': form})
    except Exception as e:
        logger.error(f"Error loading profile: {e}")
        return HttpResponseServerError("An error occurred")
    
def play_course(request):
    return render(request, 'learner/play_course.html')
    

from django.utils import timezone

@login_required
def enrolled_courses(request):
    learner = request.user.learner
    learner_timezone = pytz.timezone(learner.user.timezone)

    enrolled_deliveries = CourseDelivery.objects.filter(participants=learner)

    for delivery in enrolled_deliveries:
        creator_timezone = pytz.timezone(delivery.timezone)

        # Create datetime objects in the creator's timezone
        start_datetime = creator_timezone.localize(datetime.combine(delivery.start_date, delivery.start_time))
        end_datetime = creator_timezone.localize(datetime.combine(delivery.end_date, delivery.end_time))

        # Convert to learner's timezone
        delivery.start_datetime_local = start_datetime.astimezone(learner_timezone)
        delivery.end_datetime_local = end_datetime.astimezone(learner_timezone)

        if delivery.deactivation_date and delivery.deactivation_time:
            deactivation_datetime = creator_timezone.localize(datetime.combine(delivery.deactivation_date, delivery.deactivation_time))
            delivery.deactivation_datetime_local = deactivation_datetime.astimezone(learner_timezone)
        else:
            delivery.deactivation_datetime_local = None

        delivery.start_datetime_raw = delivery.start_datetime_local
        delivery.end_datetime_raw = delivery.end_datetime_local

        print(f"Start Datetime (Creator's TZ): {start_datetime}")
        print(f"Start Datetime (Learner's TZ): {delivery.start_datetime_local}")

    return render(request, 'learner/enrolled_deliveries.html', {
        'enrolled_deliveries': enrolled_deliveries,
        'learner_timezone': learner_timezone,
    })