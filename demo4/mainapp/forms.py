from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User

APP_CHOICES = [
    ('dashboard', 'Main Dashboard'),
    ('app1', 'App1'),
    ('app2', 'App2'),
]


class LoginForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def confirm_login_allowed(self, user):
        if not (user.is_superuser or user.groups.filter(name='admin').exists()):
            raise forms.ValidationError(
                'Only admin users can log in here.',
                code='invalid_login',
            )


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
