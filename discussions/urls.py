from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.discussions, name='learner_discussions'),
]
