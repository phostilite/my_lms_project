from django.urls import path, include

from . import views

urlpatterns = [
    path('create_course/<str:course_id>/', views.create_course, name='create_course'),
    path('register/', views.register_and_create_scorm_registration, name='register_and_create_scorm_registration'),
    path('get_launch_link/', views.get_launch_link, name='get_launch_link'),
]
