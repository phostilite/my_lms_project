from django import forms
from .models import ScormCloudCourse
from accounts.models import Facilitator, Learner
from .models import CourseDelivery, ScormCloudCourse

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


class CourseDeliveryForm(forms.ModelForm):
    class Meta:
        model = CourseDelivery
        fields = [
            'delivery_code', 'delivery_type', 'enrollment_type',
            'all_participants_access', 'facilitators', 'participants',
            'start_date', 'end_date', 'deactivation_date', 'is_mandatory',
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
        self.fields['start_date'].required = False
        self.fields['end_date'].required = False
        self.fields['deactivation_date'].required = False

        # Set initial value for delivery_code if it's a new instance
        if not self.instance.pk:
            self.fields['delivery_code'].initial = CourseDelivery.generate_unique_delivery_code()

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        deactivation_date = cleaned_data.get('deactivation_date')

        if start_date and end_date and start_date > end_date:
            raise forms.ValidationError("End date should be after the start date.")

        if end_date and deactivation_date and deactivation_date < end_date:
            raise forms.ValidationError("Deactivation date should be after the end date.")

        return cleaned_data