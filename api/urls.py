from django.urls import path, include

from . import views

urlpatterns = [
    path('create_course/<str:course_id>/', views.create_course, name='create_course'),
    path('register/', views.register_and_create_scorm_registration, name='register_and_create_scorm_registration'),
    path('scorm_cloud_operations/', views.scorm_cloud_operations, name='scorm_cloud_operations'),
    path('delete_course/<str:course_id>/', views.DeleteCourseView.as_view(), name='delete_course'),


    path('login/', views.LoginView.as_view(), name='api_login'),
    path('enrolled_courses/', views.EnrolledCoursesView.as_view(), name='enrolled_courses'),
    path('registration_id/', views.GetRegistrationIDView.as_view(), name='get_registration_id'),

    path('token/refresh/', views.RefreshTokenView.as_view(), name='token_refresh'),
]
