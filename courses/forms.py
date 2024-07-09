from django import forms
from .models import ScormCloudCourse

class ScormCloudCourseForm(forms.ModelForm):
    file = forms.FileField()
    class Meta:
        model = ScormCloudCourse
        fields = [
            'title',
            'course_id',
            'long_description', 
            'short_description', 
            'category', 
            'duration', 
            'cover_image',
            ]
