import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
import rustici_software_cloud_v2 as scorm_cloud
import time
import tempfile
import shutil
import os
import json
import zipfile
import uuid
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse, HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rustici_software_cloud_v2.rest import ApiException
from django.views import View
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404


from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken 

from courses.models import ScormCloudCourse
from .utils import course_id_is_valid
from accounts.models import Learner
from courses.models import ScormCloudCourse, ScormCloudRegistration, CourseDelivery


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from .serializers import CourseDeliverySerializer, ScormCloudRegistrationSerializer  

User = get_user_model()

logger = logging.getLogger(__name__)

@csrf_exempt
def create_course(request, course_id):
    if request.method == 'POST':
        logger.info("Received a POST request to create a course.")

        # Course ID Validation
        if not course_id_is_valid(course_id):
            return JsonResponse({'error': 'Invalid course ID format'}, status=400)
        
        course_file = request.FILES.get('file')
        if not course_file:
            logger.error("No course file provided.")
            return JsonResponse({'error': 'Course file is required'}, status=400)
        # if not zipfile.is_zipfile(course_file):
        #     return JsonResponse({'error': 'Invalid file type. Please upload a SCORM ZIP archive.'}, status=400)
        
        # Check for Existing Course
        try:
            ScormCloudCourse.objects.get(course_id=course_id)  # Query the database
            return JsonResponse({'error': 'A course with this ID already exists.'}, status=400)
        except ScormCloudCourse.DoesNotExist:
            pass  # Course doesn't exist, proceed with creation

        # Save the uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            shutil.copyfileobj(course_file.file, temp_file)
            temp_file_path = temp_file.name

        logger.info("Configuring ScormCloud API.")
        # Configure ScormCloud API
        config = scorm_cloud.Configuration()
        config.username = settings.CLOUDSCORM_APP_ID
        config.password = settings.CLOUDSCORM_SECRET_KEY
        scorm_cloud.Configuration().set_default(config)

        course_api = scorm_cloud.CourseApi()

        try:
            logger.info("Creating and importing the course.")
            # Create and import the course using the path of the temporary file
            job_id = course_api.create_upload_and_import_course_job(course_id, file=temp_file_path)

            logger.info(f"Checking job status for job ID: {job_id.result}.")
            # Check job status
            job_result = course_api.get_import_job_status(job_id.result)
            while job_result.status == "RUNNING":
                logger.info("Job is running; waiting for completion.")
                time.sleep(1)
                job_result = course_api.get_import_job_status(job_id.result)

            # Print the raw output from the job_result
            logger.info(f"Raw job result: {job_result}")

            if job_result.status == "ERROR":
                logger.error(f"Course import failed: {job_result.message}")
                return JsonResponse({'error': f"Course import failed: {job_result.message}"}, status=400)

            logger.info("Course created successfully.")

            # Extract course details from job_result
            course_data = job_result.import_result.course
            course_id = course_data.id
            title = course_data.title
            version = course_data.version
            created_at = course_data.created
            updated_at = course_data.updated
            web_path = job_result.import_result.web_path_to_course

            # Save the course details to the database
            scorm_course = ScormCloudCourse(
                course_id=course_id,
                title=title,
                version=version,
                created_at=created_at,
                updated_at=updated_at,
                web_path=web_path
            )
            scorm_course.save()

            job_result_dict = job_result.to_dict() if hasattr(job_result, 'to_dict') else {}

            return JsonResponse({'message': 'Course created successfully', 'job_result': job_result_dict})

        except scorm_cloud.rest.ApiException as e:
            logger.exception("An error occurred with the ScormCloud API.")
            return JsonResponse({'error': str(e)}, status=500)
        except Exception as e:
            logger.exception("An unexpected error occurred.")
            return JsonResponse({'error': 'An unexpected error occurred'}, status=500)
        finally:
            os.remove(temp_file_path)
    else:
        logger.warning("Received a non-POST request.")
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)

@csrf_exempt
@require_POST
def register_and_create_scorm_registration(request):
    try:
        # 1. Get Data and Validate:
        course_id = request.POST.get('course_id')
        learner_id = request.POST.get('learner_id')

        if not course_id or not learner_id:
            raise ValueError("Course ID and Learner ID are required.")

        learner = Learner.objects.get(pk=learner_id)
        course = ScormCloudCourse.objects.get(course_id=course_id)

        # 2. Check if Already Registered:
        existing_registration = ScormCloudRegistration.objects.filter(
            learner=learner, course_id=course_id
        ).exists()
        if existing_registration:
            return JsonResponse({'error': 'Learner is already registered for this course.'}, status=400)

        # 3. ScormCloud Registration:
        config = scorm_cloud.Configuration()
        config.username = settings.CLOUDSCORM_APP_ID
        config.password = settings.CLOUDSCORM_SECRET_KEY
        scorm_cloud.Configuration().set_default(config)
        registration_api = scorm_cloud.RegistrationApi()

        registration_id = str(uuid.uuid4())

        scorm_learner = scorm_cloud.LearnerSchema(
            id=str(learner.user.id),
            first_name=learner.user.first_name,
            last_name=learner.user.last_name
        )

        registration = scorm_cloud.CreateRegistrationSchema(
            course_id=course_id,
            learner=scorm_learner, 
            registration_id=registration_id,
        )
    
        # Create the registration on ScormCloud
        registration_api.create_registration(registration)
        logger.info(f"Registration for learner {learner_id} and course {course_id} sent to ScormCloud.")

        try:
            # Attempt to fetch the created registration
            created_registration = registration_api.get_registration_progress(registration_id)

            # 4. Handle ScormCloud Response:
            if created_registration is None or created_registration.id is None:
                raise Exception("ScormCloud registration failed: Unable to retrieve created registration.")

        except scorm_cloud.rest.ApiException as api_e:
            logger.error(f"ScormCloud API Error: {api_e}")
            return JsonResponse({'error': f'ScormCloud registration failed: {api_e.reason}'}, status=500)

        # 5. Save Registration in Your Database:
        registration = ScormCloudRegistration(
            registration_id=created_registration.id,
            learner=learner,
            course_id=course_id
        )
        registration.save()

        return JsonResponse({
            'message': 'Registration successful',
            'registration_id': registration.registration_id,
            'learner_id': registration.learner.pk,  
            'course_id': registration.course_id,
        })

    except Learner.DoesNotExist:
        logger.error(f"Learner with ID {learner_id} not found.")
        return JsonResponse({'error': 'Learner not found'}, status=404)
    except ScormCloudCourse.DoesNotExist:
        logger.error(f"Course with ID {course_id} not found.")
        return JsonResponse({'error': 'Course not found'}, status=404)
    except ValueError as e:
        logger.error(str(e)) 
        return JsonResponse({'error': str(e)}, status=400)
    except scorm_cloud.rest.ApiException as e:
        logger.error(f"ScormCloud API error: {e}")
        return JsonResponse({'error': 'ScormCloud registration failed'}, status=500)
    except Exception as e:
        logger.exception("Error during registration:")
        return JsonResponse({'error': 'Registration failed'}, status=500)
    

@require_http_methods(["GET", "POST"])
def scorm_cloud_operations(request):
    try:
        # ScormCloud Configuration
        config = scorm_cloud.Configuration()
        config.username = settings.CLOUDSCORM_APP_ID
        config.password = settings.CLOUDSCORM_SECRET_KEY
        scorm_cloud.Configuration().set_default(config)

        if request.method == 'GET':
            return get_launch_link(request)
        elif request.method == 'POST':
            return set_application_configuration(request)

    except Exception as e:
        logger.exception("Error in SCORM Cloud operations:")
        return JsonResponse({'error': str(e)}, status=500)
    
def get_launch_link(request):
    try:
        learner_id = request.GET.get('learner_id')
        registration_id = request.GET.get('registration_id')

        if not learner_id or not registration_id:
            raise ValueError("Learner ID and Registration ID are required.")

        # Validate learner and registration
        learner = Learner.objects.get(pk=learner_id)
        registration = ScormCloudRegistration.objects.get(registration_id=registration_id, learner=learner)

        registration_api = scorm_cloud.RegistrationApi()

        # Build Launch Link
        launch_link_request = {
            "redirectOnExitUrl": "https://your-lms.com/exit",  # Replace with your actual exit URL
            "launchAuth": {
                "type": "vault"
            },
            "expiry": 3600, 
            "tracking": True
        }
        
        launch_link_response = registration_api.build_registration_launch_link(
            registration_id=str(registration.registration_id), 
            launch_link_request=launch_link_request,
        )
        
        return JsonResponse({'launch_link': launch_link_response.launch_link})

    except (Learner.DoesNotExist, ScormCloudRegistration.DoesNotExist) as e:
        logger.error(f"Resource not found: {str(e)}")
        return JsonResponse({'error': str(e)}, status=404)
    except ValueError as e:
        logger.error(str(e))
        return JsonResponse({'error': str(e)}, status=400)
    except scorm_cloud.rest.ApiException as api_e:
        logger.error(f"ScormCloud API Error: {api_e}")
        return JsonResponse({'error': f'ScormCloud launch link generation failed: {api_e.reason}'}, status=500)

def set_application_configuration(request):
    try:
        app_management_api = scorm_cloud.ApplicationManagementApi()

        config_settings = {
            "settings": [
                {
                    "settingId": "PlayerLaunchType",
                    "value": "FRAMESET",
                    "explicit": True
                },
                {
                    "settingId": "PlayerScoLaunchType",
                    "value": "FRAMESET",
                    "explicit": True
                },
                {
                    "settingId": "LaunchAuthType",
                    "value": "vault",
                    "explicit": True
                }
            ]
        }

        response = app_management_api.set_application_configuration(config_settings)
        return JsonResponse({'message': 'Application configuration updated successfully'})

    except scorm_cloud.rest.ApiException as api_e:
        logger.error(f"ScormCloud API Error: {api_e}")
        return JsonResponse({'error': f'Failed to update application configuration: {api_e.reason}'}, status=500)
    

@method_decorator(csrf_exempt, name='dispatch')
class DeleteCourseView(View):
    def delete(self, request, course_id):
        try:
            # Configure SCORM Cloud client
            config = scorm_cloud.Configuration()
            config.username = settings.CLOUDSCORM_APP_ID
            config.password = settings.CLOUDSCORM_SECRET_KEY
            scorm_cloud.Configuration().set_default(config)
            
            # Initialize CourseApi
            course_api = scorm_cloud.CourseApi()
            
            # Delete the course
            course_api.delete_course(course_id)
            
            # Delete the course from local database
            try:
                scorm_course = ScormCloudCourse.objects.get(course_id=course_id)
                scorm_course.delete()
                logger.info(f"Course with ID {course_id} has been successfully deleted from SCORM Cloud and local database.")
            except ObjectDoesNotExist:
                logger.warning(f"Course with ID {course_id} was deleted from SCORM Cloud but not found in local database.")
            
            return JsonResponse({"message": "Course deleted successfully from SCORM Cloud and local database"}, status=200)
        
        except ApiException as e:
            logger.error(f"API error occurred while deleting course {course_id} from SCORM Cloud: {str(e)}")
            return JsonResponse({"error": "API error occurred", "details": str(e)}, status=500)
        
        except ValueError as e:
            logger.error(f"Value error occurred while deleting course {course_id}: {str(e)}")
            return JsonResponse({"error": "Invalid course ID", "details": str(e)}, status=400)
        
        except Exception as e:
            logger.error(f"Unexpected error occurred while deleting course {course_id}: {str(e)}")
            return JsonResponse({"error": "An unexpected error occurred", "details": str(e)}, status=500)



class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Input validation
        if not email or not password:
            return Response({'error': 'Please provide both email and password.'}, status=status.HTTP_400_BAD_REQUEST)

        # User authentication
        user = authenticate(request, username=email, password=password)

        if user is not None:
            refresh = RefreshToken.for_user(user)  
            access_token = str(refresh.access_token)
            refresh_token = str(refresh)

            groups = list(user.groups.values_list('name', flat=True)) 

            try:
                learner = Learner.objects.get(user=user)
                learner_id = learner.id
            except Learner.DoesNotExist:
                learner_id = None  

            response_data = {
                'message': 'Login successful',
                'access': access_token,
                'refresh': refresh_token,
                'groups': groups,
                'learner_id': learner_id,
                'learner_name': user.get_full_name() if user.get_full_name() else None,
                'learner_email': user.email if user.email else None,
                'learner_phone': user.phone_number if user.phone_number else None,
                'learner_picture': request.build_absolute_uri(user.picture.url) if user.picture else None,
                'learner_date_joined': user.date_joined,
                'learner_gender': user.gender,
                'learner_timezone': user.timezone,
            }
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)



class EnrolledCoursesView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        learner = request.user.learner
        enrolled_deliveries = CourseDelivery.objects.filter(participants=learner)
        serializer = CourseDeliverySerializer(enrolled_deliveries, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    
class GetRegistrationIDView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        learner_id = request.query_params.get('learner_id')
        course_id = request.query_params.get('course_id')

        if not learner_id or not course_id:
            return Response({"error": "learner_id and course_id must be provided."}, status=status.HTTP_400_BAD_REQUEST)

        # Assuming 'Learner' model has an 'id' field that matches 'learner_id'
        registration = get_object_or_404(ScormCloudRegistration, learner__id=learner_id, course_id=course_id)
        serializer = ScormCloudRegistrationSerializer(registration)
        return Response(serializer.data, status=status.HTTP_200_OK)