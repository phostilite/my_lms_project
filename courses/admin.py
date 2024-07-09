from django.contrib import admin

from . models import ScormCloudCourse, ScormCloudRegistration, CourseDelivery, Enrollment, Feedback, Attendance

admin.site.register(ScormCloudCourse)
admin.site.register(ScormCloudRegistration)
admin.site.register(CourseDelivery)
admin.site.register(Enrollment)
admin.site.register(Feedback)
admin.site.register(Attendance)