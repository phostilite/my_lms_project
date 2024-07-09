from django.forms import ValidationError
from django.http import HttpResponseServerError
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
import requests
from django.conf import settings
from django.shortcuts import redirect
import logging
from decimal import Decimal
from django.db import transaction
from django.db import IntegrityError, transaction
from django.contrib import messages
from django.contrib.auth import get_user_model

from courses.models import ScormCloudCourse
from courses.forms import ScormCloudCourseForm
from accounts.models import Learner, Supervisor
from learner.forms import LearnerForm
from supervisor.forms import SupervisorForm

logger = logging.getLogger(__name__)

User = get_user_model()

@login_required
def dashboard(request):
    try:
        return render(request, 'administrator/dashboard.html')
    except Exception as e:
        logger.error(f"Error loading dashboard: {e}")
        return HttpResponseServerError("An error occurred")
    
@login_required
def calendar(request):
    try:
        return render(request, 'administrator/calendar.html')
    except Exception as e:
        logger.error(f"Error loading calendar: {e}")
        return HttpResponseServerError("An error occurred")

@login_required
def leaderboard(request):
    try:
        return render(request, 'administrator/leaderboard.html')
    except Exception as e:
        logger.error(f"Error loading leaderboard: {e}")
        return HttpResponseServerError("An error occurred")

@login_required
def course_list(request):
    try:
        courses = ScormCloudCourse.objects.all()
    except ScormCloudCourse.DoesNotExist:
        courses = None
    return render(request, 'administrator/course_list.html', {'courses': courses})

@login_required
def upload_course(request):
    if request.method == 'POST':
        form = ScormCloudCourseForm(request.POST, request.FILES)
        if form.is_valid():
            course_id = form.cleaned_data['course_id']
            file = form.cleaned_data['file']

            category = form.cleaned_data.get('category', '')
            duration = form.cleaned_data.get('duration', '')
            price = form.cleaned_data.get('price', Decimal('0.00'))
            short_description = form.cleaned_data.get('short_description', '')
            long_description = form.cleaned_data.get('long_description', '')
            cover_image = form.cleaned_data.get('cover_image', '')

            files = {'file': file}

            try:
                response = requests.post(
                    f'{settings.DOMAIN_NAME}/api/create_course/{course_id}/',
                    files=files,
                )

                response.raise_for_status()  # Raise exception for bad responses (4xx and 5xx)
                api_response_data = response.json()

                if api_response_data.get('message') == 'Course created successfully':
                    # Fetch or create the ScormCloudCourse object
                    course, created = ScormCloudCourse.objects.get_or_create(
                        course_id=course_id, 
                        defaults={
                            'title': form.cleaned_data['title'],
                            'version': api_response_data.get('version', ''),
                            'web_path': api_response_data.get('web_path_to_course', '')  
                        }
                    )
                    # Update only if already exists or new
                    if not created:
                        course.category = category
                        course.duration = duration
                        course.short_description = short_description
                        course.long_description = long_description
                        course.cover_image = cover_image
                        course.save()

                    # Log Success (with more details)
                    logger.info(f"Course created/updated successfully: {course_id}, Response: {api_response_data}")

                    return redirect('course_list')  # Redirect to your course list view

                else:
                    # Handle API errors with more detailed logging
                    error_msg = api_response_data.get('error', 'Unknown error')
                    logger.error(f"Course creation API failed: {error_msg}")
                    form.add_error(None, error_msg)  # Add the error to the form

            except requests.RequestException as e:
                logger.exception("Error calling create_course API:")  # Log full exception traceback
                form.add_error(None, f"Error creating course: {e}")
            except ScormCloudCourse.DoesNotExist:
                logger.error(f"Course with ID {course_id} not found after API call.")
                form.add_error(None, "Course not found in database after creation.")
    
    else:
        form = ScormCloudCourseForm()
    return render(request, 'administrator/upload_course.html', {'form': form})


@login_required
def settings(request):
    try:
        return render(request, 'administrator/settings.html')
    except Exception as e:
        logger.error(f"Error loading profile: {e}")
        return HttpResponseServerError("An error occurred")
    
def learner_list(request):
    try:
        learners = Learner.objects.all()
    except Learner.DoesNotExist:
        learners = None
    return render(request, 'administrator/learner_list.html', {'learners': learners})

def supervisor_list(request):
    try:
        supervisors = Supervisor.objects.all()
    except Supervisor.DoesNotExist:
        supervisors = None
    return render(request, 'administrator/supervisor_list.html', {'supervisors': supervisors})


@transaction.atomic
def register_learner(request):
    if request.method == 'POST':
        form = LearnerForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(request, 'Learner registered successfully!')
                return redirect('administrator_learner_list')
            except IntegrityError:
                messages.error(request, 'A learner with this email already exists.')
                # Explicitly return to avoid further operations in the same transaction block
                return render(request, 'administrator/register_learner.html', {'form': form})
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f'{field.capitalize()}: {error}')
                # Return here if you want to stop further processing and show the form again
                return render(request, 'administrator/register_learner.html', {'form': form})
            except Exception as e:
                logger.error(f'Error registering learner: {e}')
                messages.error(request, 'An error occurred during registration. Please try again.')
                # Return here to handle any other exceptions and stop further processing
                return render(request, 'administrator/register_learner.html', {'form': form})
        else:
            # Iterate through form errors and add them as messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')
    else:
        form = LearnerForm()

    return render(request, 'administrator/register_learner.html', {'form': form})

@transaction.atomic
def register_supervisor(request):
    if request.method == 'POST':
        form = SupervisorForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    form.save()
                messages.success(request, 'Supervisor registered successfully!')
                return redirect('administrator_supervisor_list')
            except IntegrityError:
                messages.error(request, 'A supervisor with this email already exists.')
                # Explicitly return to avoid further operations in the same transaction block
                return render(request, 'administrator/register_supervisor.html', {'form': form})
            except ValidationError as e:
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f'{field.capitalize()}: {error}')
                # Return here if you want to stop further processing and show the form again
                return render(request, 'administrator/register_supervisor.html', {'form': form})
            except Exception as e:
                logger.error(f'Error registering supervisor: {e}')
                messages.error(request, 'An error occurred during registration. Please try again.')
                # Return here to handle any other exceptions and stop further processing
                return render(request, 'administrator/register_supervisor.html', {'form': form})
        else:
            # Iterate through form errors and add them as messages
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'{field.capitalize()}: {error}')
    else:
        form = SupervisorForm()

    return render(request, 'administrator/register_supervisor.html', {'form': form})


def enrollment_activity(request):
    try:
        return render(request, 'administrator/enrollment_activity.html')
    except Exception as e:
        logger.error(f"Error loading enrollment_activity: {e}")
        return HttpResponseServerError("An error occurred")
    
def progress_performance(request):
    try:
        return render(request, 'administrator/progress_performance.html')
    except Exception as e:
        logger.error(f"Error loading progress_performance: {e}")
        return HttpResponseServerError("An error occurred")
    
def engagement_feedback(request):
    try:
        return render(request, 'administrator/engagement_feedback.html')
    except Exception as e:
        logger.error(f"Error loading engagement_feedback: {e}")
        return HttpResponseServerError("An error occurred")

def system_usuage(request):
    try:
        return render(request, 'administrator/system_usuage.html')
    except Exception as e:
        logger.error(f"Error loading system_usuage: {e}")
        return HttpResponseServerError("An error occurred")