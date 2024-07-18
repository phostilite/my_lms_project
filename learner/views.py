# Standard library imports
from datetime import datetime
import logging

# Third-party imports
import base64
from django.conf import settings as django_settings
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseServerError, JsonResponse
from django.shortcuts import redirect, render, get_object_or_404
import pytz
import requests

# Local application/library specific imports
from accounts.forms import UserTimeZoneForm
from accounts.models import Learner
from learner.forms import LearnerForm, LearnerNameForm, LearnerEmailForm, LearnerProfilePictureForm
from courses.models import CourseDelivery, ScormCloudCourse, ScormCloudRegistration

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
    return render(request, 'learner/courses/catalog.html', {'courses': courses})

@login_required
def course_details(request, course_id):
    try:
        course = ScormCloudCourse.objects.get(id=course_id)
        return render(request, 'learner/courses/details.html', {'course': course})
    except ScormCloudCourse.DoesNotExist:
        raise Http404("Course not found")
    except Exception as e:
        logger.error(f"Error loading course details: {e}")
        return HttpResponseServerError("An error occurred")

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
def learner_settings(request):
    forms = {
        'timezone_form': UserTimeZoneForm(prefix='timezone_form', instance=request.user),
        'learner_name_form': LearnerNameForm(prefix='learner_name_form', instance=request.user),
        'learner_email_form': LearnerEmailForm(prefix='learner_email_form', instance=request.user),
        'profile_picture_form': LearnerProfilePictureForm(prefix='profile_picture_form', instance=request.user),
    }

    try:
        if request.method == 'POST':
            # Identify which form is being submitted
            for form_name, form in forms.items():
                if form_name in request.POST:
                    if form_name == 'profile_picture_form':
                        form = form.__class__(request.POST, request.FILES, instance=request.user, prefix=form_name)
                    else:
                        form = form.__class__(request.POST, instance=request.user, prefix=form_name)
                    if form.is_valid():
                        form.save()
                        return redirect('learner_settings')
                    else:
                        logger.error(f"Form errors in {form_name}: {form.errors.as_json()}")
                        forms[form_name] = form
                        break  

        return render(request, 'learner/settings.html', {'forms': forms})

    except Exception as e:
        logger.error(f"Error loading profile: {e}")
        return HttpResponseServerError("An error occurred")
    

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
        'learner': learner,
    })


def launch_course(request):
    return render(request, 'learner/launch_course.html')

def play_course(request):
    try:
        # Extract learner_id and delivery_id from the request
        learner_id = request.GET.get('learner_id')
        delivery_id = request.GET.get('delivery_id')

        # Validate and fetch the Learner object
        learner = get_object_or_404(Learner, id=learner_id)

        # Validate and fetch the CourseDelivery object
        delivery = get_object_or_404(CourseDelivery, id=delivery_id)

        # Validate if the delivery belongs to the requested course
        if not delivery.course:
            raise ValueError("The delivery does not have an associated course.")

        # Fetch the ScormCloudCourse using the course from delivery
        course = get_object_or_404(ScormCloudCourse, id=delivery.course.id)

        # Validate and fetch the ScormCloudRegistration object
        registration = get_object_or_404(ScormCloudRegistration, learner=learner, course_id=course.course_id)

        # Prepare context data for rendering
        context = {
            'learner_id': learner_id,
            'registration_id': registration.registration_id,
            'course': course,
            'delivery': delivery,
        }

        return render(request, 'learner/play_course.html', context)

    except Http404 as e:
        logger.error(f"Resource not found: {str(e)}")
        return JsonResponse({'error': 'Resource not found'}, status=404)
    except ValueError as e:
        logger.error(str(e))
        return JsonResponse({'error': str(e)}, status=400)
    except Exception as e:
        logger.exception("Unexpected error occurred while launching the course.")
        return JsonResponse({'error': 'An unexpected error occurred'}, status=500)



def support(request):
    try:
        return render(request, 'learner/support.html')
    except Exception as e:
        logger.error(f"Error loading support: {e}")
        return HttpResponseServerError("An error occurred")