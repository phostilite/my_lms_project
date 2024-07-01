from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    phone_number = models.CharField(max_length=15, default='')
    gender = models.CharField(max_length=10, choices=[('male', 'Male'), ('female', 'Female'), ('other', 'Other')],
                              default='male')
    picture = models.ImageField(upload_to='user_pictures/', blank=True, null=True)


class Learner(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Learner-specific fields (e.g., enrollment_date, courses_enrolled)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class Instructor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Instructor-specific fields (e.g., bio, qualifications)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name


class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Administrator-specific fields (if needed)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
