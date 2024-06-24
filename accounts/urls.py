from django.urls import path, include
from django.contrib.auth import views as auth_views  

from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('accounts/signup/', views.LearnerSignupView.as_view(), name='signup'),
]
