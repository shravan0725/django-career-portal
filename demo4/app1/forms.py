from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from .models import App1Data, App1Login


class App1DataForm(forms.ModelForm):
    class Meta:
        model = App1Data
        fields = ['title', 'description']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


class App1SignupForm(UserCreationForm):
    user_id = forms.CharField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['user_id', 'username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_user_id(self):
        user_id = self.cleaned_data['user_id']
        if App1Login.objects.filter(user_id=user_id).exists():
            raise forms.ValidationError('This user ID is already taken in App1.')
        return user_id

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class App1AuthenticationForm(forms.Form):
    user_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    error_messages = {
        'invalid_login': 'Invalid user or credentials. Please register first.',
    }

    def clean(self):
        cleaned_data = super().clean()
        user_id = cleaned_data.get('user_id')
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if user_id and username and password:
            try:
                login_record = App1Login.objects.get(user_id=user_id, username=username)
            except App1Login.DoesNotExist:
                raise forms.ValidationError(self.error_messages['invalid_login'])

            if not check_password(password, login_record.password):
                raise forms.ValidationError(self.error_messages['invalid_login'])

            user = authenticate(username=username, password=password)
            if user is None:
                raise forms.ValidationError(self.error_messages['invalid_login'])
            self.user_cache = user

        return cleaned_data

    def get_user(self):
        return getattr(self, 'user_cache', None)


class App1LoginForm(forms.ModelForm):
    user_id = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = App1Login
        fields = ['user_id', 'username', 'password']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.password = make_password(self.cleaned_data['password'])
        if commit:
            instance.save()
        return instance
