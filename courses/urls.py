from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.course_catalog, name='learner_course_catalog'),
]
