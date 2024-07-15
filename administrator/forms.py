from django import forms
from django.contrib.auth.models import User, Group
from accounts.models import Learner
from django.contrib.auth import get_user_model

User = get_user_model()

class AdminNameForm(forms.ModelForm):
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

class AdminEmailForm(forms.ModelForm):
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


class AdminProfilePictureForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['picture']
        widgets = {
            'picture': forms.FileInput(attrs={'class': 'hidden', 'accept': 'image/*'}),
        }