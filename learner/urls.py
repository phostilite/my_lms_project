from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name='learner_dashboard'),
    path('calendar/', views.calendar, name='learner_calendar'),
    path('courses/', views.courses, name='learner_courses'),
    path('course_catalog', views.course_catalog, name='learner_course_catalog'),
    path('certificates/', views.certificates, name='learner_certificates'),
    path('badge/', views.badge, name='learner_badge'),
    path('leaderboard/', views.leaderboard, name='learner_leaderboard')
]