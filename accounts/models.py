from django.db import models
from django.contrib.auth.models import AbstractUser
import pytz
from django.utils import timezone

class User(AbstractUser):
    
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                              default='male')
    picture = models.ImageField(upload_to='user_pictures/', blank=True, null=True)
    timezone = models.CharField(
        max_length=50, 
        choices=[(tz, tz) for tz in pytz.common_timezones],
        default=timezone.get_current_timezone_name()
    )


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
    

class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class Supervisor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
    
class Facilitator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name