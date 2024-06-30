from django.contrib import admin

from . models import ScormCloudCourse, ScormCloudRegistration

admin.site.register(ScormCloudCourse)
admin.site.register(ScormCloudRegistration)