from django import forms
from django.contrib.auth.models import User, Group
from accounts.models import Learner
from django.contrib.auth import get_user_model

User = get_user_model()

class LearnerForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput())
    phone = forms.CharField(max_length=15)
    gender = forms.ChoiceField(choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')])

    class Meta:
        model = Learner
        fields = ('phone', 'gender')

    def save(self, commit=True):
        user = User.objects.create_user(
            username=self.cleaned_data['email'],  
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )

        group, created = Group.objects.get_or_create(name='learner')
        user.groups.add(group)

        learner = super().save(commit=False)
        learner.user = user
        if commit:
            learner.save()
        return learner
    

class LearnerNameForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)

    class Meta:
        model = User
        fields = ('first_name', 'last_name')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class LearnerEmailForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ('email',)

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class LearnerProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['picture']
        widgets = {
            'picture': forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'}),
        }