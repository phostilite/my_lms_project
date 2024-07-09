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
    path('microsoft_signin/', views.microsoft_sign_in, name='microsoft_signin'),
    path('microsoft_signup/', views.microsoft_sign_up, name='microsoft_signup'),

    path('callback/', views.microsoft_callback, name='callback'),

    path('google_auth', views.google_auth, name='google_auth'),
    path('google/callback', views.google_auth_callback, name='google_callback'),  

    path('password-reset/', views.ResetPasswordView.as_view(), name='password_reset'),
    path('password-reset-confirm/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='resets/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('password-reset-complete/',
         auth_views.PasswordResetCompleteView.as_view(template_name='resets/password_reset_complete.html'),
         name='password_reset_complete'),
]