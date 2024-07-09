from django import forms
from django.contrib.auth.models import User, Group
from accounts.models import Supervisor
from django.contrib.auth import get_user_model

User = get_user_model()

class SupervisorForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    phone = forms.CharField(max_length=15)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])

    class Meta:
        model = Supervisor
        fields = ('phone', 'gender')

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],  
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )

        group, created = Group.objects.get_or_create(name='supervisor')
        user.groups.add(group)

        supervisor = super().save(commit=False)
        supervisor.user = user
        if commit:
            supervisor.save()
        return supervisor