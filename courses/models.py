from django.conf import settings
from django.db import models
import uuid
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import dateutil.relativedelta

import random
import string


from accounts.models import Learner, Facilitator

User = get_user_model()

class ScormCloudCourse(models.Model):
    course_id = models.CharField(max_length=50, unique=True)  
    title = models.CharField(max_length=255)
    version = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    web_path = models.CharField(max_length=255, null=True, blank=True)  

    long_description = models.TextField(null=True, blank=True)
    short_description = models.CharField(max_length=500, null=True, blank=True)  
    category = models.CharField(max_length=100, null=True, blank=True)  
    duration = models.DurationField(null=True, blank=True) 
    cover_image = models.ImageField(upload_to='course_covers/', null=True, blank=True)
    published_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.DO_NOTHING, related_name='published_courses',
    null=True, blank=True)   
    registration_id = models.CharField(max_length=255, null=True, blank=True) 

    def __str__(self):
        return f"Course: {self.title} (ID: {self.course_id})"

class ScormCloudRegistration(models.Model):
    registration_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Registration {self.registration_id} for {self.learner}"
    

class CourseDelivery(models.Model):
    DELIVERY_TYPES = (
        ('SELF_PACED', 'Self Paced'),
        ('INSTRUCTOR_LED', 'Instructor Led'),
    )
    ENROLLMENT_TYPES = (
        ('OPEN', 'Open Enrollment'),
        ('INVITE', 'By Invitation'),
    )
    STATUS = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    )

    title = models.CharField(max_length=255, null=True, blank=True)
    course = models.ForeignKey(ScormCloudCourse, on_delete=models.CASCADE, related_name='deliveries')
    delivery_code = models.CharField(max_length=50, unique=True)
    delivery_type = models.CharField(max_length=20, choices=DELIVERY_TYPES)
    enrollment_type = models.CharField(max_length=20, choices=ENROLLMENT_TYPES)
    all_participants_access = models.BooleanField(default=True)
    facilitators = models.ManyToManyField(Facilitator, related_name='facilitated_deliveries')
    participants = models.ManyToManyField(Learner, related_name='enrolled_deliveries')
    start_date = models.DateField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    deactivation_date = models.DateField(null=True, blank=True)
    deactivation_time = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')
    is_mandatory = models.BooleanField(default=False)
    requires_attendance = models.BooleanField(default=False)
    requires_feedback = models.BooleanField(default=False)
    requires_completion_certificate = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name='created_deliveries', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='ACTIVE')

    @classmethod
    def generate_unique_delivery_code(cls):
        while True:
            code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
            if not cls.objects.filter(delivery_code=code).exists():
                return code
            
    def duration(self):
        if not self.start_date or not self.end_date or not self.start_time or not self.end_time:
            return "Not available"

        start_datetime = datetime.combine(self.start_date, self.start_time)
        end_datetime = datetime.combine(self.end_date, self.end_time)
        delta = end_datetime - start_datetime

        if delta < timedelta(days=1):
            hours = delta.seconds // 3600
            return f"{hours} Hours" if hours != 1 else "1 Hour"

        if delta < timedelta(weeks=1):
            days = delta.days
            return f"{days} Days" if days != 1 else "1 Day"

        # For durations longer than a week, use dateutil's relativedelta
        diff = dateutil.relativedelta.relativedelta(end_datetime, start_datetime)
        years, months, weeks, days = diff.years, diff.months, diff.weeks, diff.days

        # Adjust days to be the remainder after accounting for full weeks
        total_days = (end_datetime - start_datetime).days
        weeks, days = divmod(total_days, 7)

        readable = []
        if years:
            readable.append(f"{years} Years" if years != 1 else "1 Year")
        if months:
            readable.append(f"{months} Months" if months != 1 else "1 Month")
        if weeks:
            readable.append(f"{weeks} Weeks" if weeks != 1 else "1 Week")
        if days:
            readable.append(f"{days} Days" if days != 1 else "1 Day")

        return ", ".join(readable)

    def __str__(self):
        return f"Course Delivery: (Code: {self.delivery_code})"
    

class Enrollment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_delivery = models.ForeignKey(CourseDelivery, on_delete=models.CASCADE)
    enrollment_date = models.DateTimeField(auto_now_add=True)
    completion_date = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course_delivery')

    def __str__(self):
        return f"{self.user.username} - {self.course_delivery.delivery_code}"
    

class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_delivery = models.ForeignKey(CourseDelivery, on_delete=models.CASCADE)
    rating = models.IntegerField()
    comments = models.TextField()
    submission_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'course_delivery')

    def __str__(self):
        return f"Feedback for {self.course_delivery.delivery_code} by {self.user.username}"
    
    
class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course_delivery = models.ForeignKey(CourseDelivery, on_delete=models.CASCADE)
    date = models.DateField()
    is_present = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user', 'course_delivery', 'date')

    def __str__(self):
        return f"{self.user.username} - {self.course_delivery.delivery_code} - {self.date}"