from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name='learner_dashboard'),
    path('calendar/', views.calendar, name='learner_calendar'),
    path('my_courses/', views.my_courses, name='learner_my_courses'),
     path('my_certificates/', views.my_certificates, name='learner_my_certificates'),
     path('my_badge/', views.my_badge, name='learner_my_badge')
]
