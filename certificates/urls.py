from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.certificates, name='learner_certificates'),
]
