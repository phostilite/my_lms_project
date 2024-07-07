from django.urls import path, include
from django.contrib.auth import views as auth_views  

from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('courses/', views.courses, name='courses'),
    path('privacy_policy/', views.privacy_policy, name='privacy_policy'),
    
    # Django Authentication
    path('accounts/login/', views.LoginView.as_view(), name='login'),
    path('accounts/logout/', views.user_logout, name='logout'),
    path('accounts/signup/', views.LearnerSignupView.as_view(), name='signup'),

    # Google OAuth2
    path('oauth/', include('social_django.urls', namespace='social')),

    # Microsoft OAuth2
    path('signin', views.microsoft_sign_in, name='signin'),
    path('callback', views.callback, name='callback'),
]
