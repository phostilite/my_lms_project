from django import forms
from .models import TenantRequest

class TenantRequestForm(forms.ModelForm):
    class Meta:
        model = TenantRequest
        fields = ['company_name', 'subdomain', 'logo', 'primary_color', 'secondary_color',
                  'db_type', 'db_name', 'db_user', 'db_password', 'db_host', 'db_port', 'cloudscorm_app_id', 'cloudscorm_secret_key']
        widgets = {
            'db_password': forms.PasswordInput(),
            'cloudscorm_secret_key': forms.PasswordInput(),
            'primary_color': forms.TextInput(attrs={'type': 'color'}),
            'secondary_color': forms.TextInput(attrs={'type': 'color'}),
        }

    def clean_db_port(self):
        db_type = self.cleaned_data.get('db_type')
        db_port = self.cleaned_data.get('db_port')
        if db_type == 'postgresql' and db_port != 5432:
            raise forms.ValidationError("Default PostgreSQL port is 5432.")
        elif db_type == 'mysql' and db_port != 3306:
            raise forms.ValidationError("Default MySQL port is 3306.")
        return db_port