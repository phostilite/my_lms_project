from django import forms
from .models import ScormCloudCourse
from accounts.models import Facilitator, Learner
from .models import CourseDelivery, ScormCloudCourse
from datetime import datetime
from django.db.models import Max
import re

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

    def __init__(self, *args, **kwargs):
        super(ScormCloudCourseForm, self).__init__(*args, **kwargs)
        # Fetch the highest course_id from the database
        max_course_id = ScormCloudCourse.objects.aggregate(Max('course_id'))['course_id__max']
        if max_course_id:
            # Extract the numeric part of the course_id
            max_id_num = int(re.search(r'\d+', max_course_id).group())
        else:
            max_id_num = 0
        # Increment the numeric part to generate the new course_id
        new_course_id = f"COURSE-{max_id_num + 1:06d}"
        # Set the initial value for the course_id field
        self.fields['course_id'].initial = new_course_id
        # Make the course_id field read-only if you don't want it to be editable
        self.fields['course_id'].disabled = True


class CourseDeliveryForm(forms.ModelForm):
    start_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    end_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))
    deactivation_time = forms.TimeField(required=False, widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = CourseDelivery
        fields = [
            'delivery_code', 'delivery_type', 'enrollment_type',
            'all_participants_access', 'facilitators', 'participants',
            'start_date', 'start_time', 'end_date', 'end_time', 
            'deactivation_date', 'deactivation_time', 'is_mandatory',
            'requires_attendance', 'requires_feedback', 'requires_completion_certificate'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'deactivation_date': forms.DateInput(attrs={'type': 'date'}),
            'facilitators': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
            'participants': forms.SelectMultiple(attrs={'class': 'form-multiselect'}),
            'delivery_code': forms.TextInput(attrs={'readonly': 'readonly'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['facilitators'].queryset = Facilitator.objects.all()
        self.fields['participants'].queryset = Learner.objects.all()

        # Make some fields optional
        self.fields['facilitators'].required = False
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
        self.fields['deactivation_date'].required = False
        self.fields['start_time'].required = False
        self.fields['end_time'].required = False
        self.fields['deactivation_time'].required = False

        # Set initial value for delivery_code if it's a new instance
        if not self.instance.pk:
            self.fields['delivery_code'].initial = CourseDelivery.generate_unique_delivery_code()

        # Set initial values for time fields if the instance has them
        if self.instance.pk:
            if hasattr(self.instance, 'start_time'):
                self.fields['start_time'].initial = self.instance.start_time
            if hasattr(self.instance, 'end_time'):
                self.fields['end_time'].initial = self.instance.end_time
            if hasattr(self.instance, 'deactivation_time'):
                self.fields['deactivation_time'].initial = self.instance.deactivation_time

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        start_time = cleaned_data.get('start_time')
        end_date = cleaned_data.get('end_date')
        end_time = cleaned_data.get('end_time')
        deactivation_date = cleaned_data.get('deactivation_date')
        deactivation_time = cleaned_data.get('deactivation_time')

        # Add any validation logic here if needed
        # For example, you might want to ensure that if a date is provided, a time is also provided

        return cleaned_data