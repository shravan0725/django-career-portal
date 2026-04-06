from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

from .models import App2Data


class App2SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class App2AuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'autofocus': True}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))


class App2DataForm(forms.ModelForm):
    class Meta:
        model = App2Data
        fields = ['full_name', 'email', 'phone', 'department', 'role', 'resume']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-control', 'id': 'department-select'}),
            'role': forms.Select(attrs={'class': 'form-control', 'id': 'role-select'}),
            'resume': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        department = cleaned_data.get('department')
        role = cleaned_data.get('role')

        valid_roles = {
            'Cloud': {'Cloud Engineer', 'DevOps Engineer', 'Cloud Architect'},
            'IT': {'Software Developer', 'Full Stack Developer', 'Data Analyst/Data Scientist'},
            'Networking': {'Network Engineer', 'Network Administrator'},
        }

        if department and role and role not in valid_roles.get(department, set()):
            raise forms.ValidationError('Selected role does not match the chosen department.')

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
