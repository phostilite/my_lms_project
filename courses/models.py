from django.db import models
import uuid

from accounts.models import Learner

class ScormCloudCourse(models.Model):
    course_id = models.CharField(max_length=50, unique=True)  
    title = models.CharField(max_length=255)
    version = models.IntegerField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    web_path = models.CharField(max_length=255, null=True, blank=True)  

    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    long_description = models.TextField(null=True, blank=True)
    short_description = models.CharField(max_length=500, null=True, blank=True)  
    category = models.CharField(max_length=100, null=True, blank=True)  
    duration = models.DurationField(null=True, blank=True) 
    cover_image = models.ImageField(upload_to='course_covers/', null=True, blank=True)

    def __str__(self):
        return f"Course: {self.title} (ID: {self.course_id})"

class ScormCloudRegistration(models.Model):
    registration_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  
    learner = models.ForeignKey(Learner, on_delete=models.CASCADE)
    course_id = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Registration {self.registration_id} for {self.learner}"