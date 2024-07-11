from django.urls import path, include

from . import views

urlpatterns = [
    path('', views.dashboard, name='administrator_dashboard'),
    path('calendar/', views.calendar, name='administrator_calendar'),
    path('course_list/', views.course_list, name='course_list'),
    path('upload_course/', views.upload_course, name='upload_course'),
    path('leaderboard/', views.leaderboard, name='administrator_leaderboard'),
    path('settings/', views.settings,   name='administrator_settings'),

    path('supervisor_list/', views.supervisor_list, name='administrator_supervisor_list'),
    path('register_supervisor/', views.register_supervisor, name='administrator_register_supervisor'),

    path('learner_list/', views.learner_list, name='administrator_learner_list'),
    path('register_learner/', views.register_learner, name='administrator_register_learner'),

    path('enrollment_activity/', views.enrollment_activity, name='administrator_enrollment_activity'),
    path('progress_performance/', views.progress_performance, name='administrator_progress_performance'),
    path('engagement_feedback/', views.engagement_feedback, name='administrator_engagement_feedback'),
    path('system_usuage/', views.system_usuage, name='administrator_system_usuage'),

    path('course_delivery/<int:pk>/list/', views.course_delivery_list, name='course_delivery_list'),
    path('course_delivery/<int:pk>/create/', views.CourseDeliveryCreateView.as_view(), name='course_delivery_create'),
    path('course_delivery/<int:course_id>/<str:delivery_id>/', views.course_delivery_detail, name='course_delivery_detail'),
    path('export_attendance/<int:delivery_id>/', views.export_attendance, name='export_attendance'),

]