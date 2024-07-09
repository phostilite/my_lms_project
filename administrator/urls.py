from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name='administrator_dashboard'),
    path('calendar/', views.calendar, name='administrator_calendar'),
    path('course_list/', views.course_list, name='course_list'),
    path('upload_course/', views.upload_course, name='upload_course'),
    path('leaderboard/', views.leaderboard, name='administrator_leaderboard'),
    path('settings/', views.settings,   name='administrator_settings')
]