from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name='learner_dashboard'),
    path('calendar/', views.calendar, name='learner_calendar'),
    path('courses/', views.courses, name='learner_courses'),
    path('course_catalog', views.course_catalog, name='learner_course_catalog'),
    path('certificates/', views.certificates, name='learner_certificates'),
    path('badge/', views.badge, name='learner_badge'),
    path('leaderboard/', views.leaderboard, name='learner_leaderboard'),
    path('progress/', views.progress, name='learner_progress'),
    path('settings/', views.settings, name='learner_settings'),

    path('enrolled_courses/', views.enrolled_courses, name='learner_enrolled_courses'),
    path('play_course/', views.play_course, name='learner_play_course'),
    path('launch_course/', views.launch_course, name='learner_launch_course'),
]