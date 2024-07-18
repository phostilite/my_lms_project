from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name='learner_dashboard'),
    path('calendar/', views.calendar, name='learner_calendar'),

    path('course_catalog', views.course_catalog, name='learner_course_catalog'),
    path('course_details/<int:course_id>', views.course_details, name='learner_course_details'),


    path('certificates/', views.certificates, name='learner_certificates'),
    path('badge/', views.badge, name='learner_badge'),
    path('leaderboard/', views.leaderboard, name='learner_leaderboard'),
    path('progress/', views.progress, name='learner_progress'),
    path('settings/', views.learner_settings, name='learner_settings'),

    path('enrolled_courses/', views.enrolled_courses, name='learner_enrolled_courses'),
    path('play_course/', views.play_course, name='learner_play_course'),
    path('launch_course/', views.launch_course, name='learner_launch_course'),

    path('support/', views.support, name='learner_support'),
]