from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.assignments, name='learner_assignments'),
]
