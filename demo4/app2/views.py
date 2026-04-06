import datetime
from functools import wraps

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group, User
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import App2AuthenticationForm, App2DataForm, App2SignupForm, UserProfileForm
from .models import App2Data, STATUS_CHOICES


class App2OwnerMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return (
            self.request.user == obj.user
            or self.request.user.groups.filter(name__in=['admin', 'hr']).exists()
            or self.request.user.is_superuser
        )


def home(request):
    if request.user.is_authenticated:
        return redirect('app2-dashboard')
    return redirect('app2-login')


def hr_login_view(request):
    if request.user.is_authenticated:
        return redirect('app2-dashboard')

    form = App2AuthenticationForm(request=request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user.groups.filter(name__in=['hr', 'admin']).exists() or user.is_superuser:
            login(request, user)
            return redirect('app2-dashboard')
        form.add_error(None, 'This login route is reserved for HR users. If you are a regular user, please use the User Login page.')

    return render(request, 'app2/login.html', {
        'form': form,
        'title': 'HR Login',
        'caption': 'HR staff can manage employee records with limited access compared to admin.',
    })


def app2_login_view(request):
    if request.user.is_authenticated:
        return redirect('app2-dashboard')

    form = App2AuthenticationForm(request=request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user.groups.filter(name='user').exists():
            login(request, user)
            return redirect('app2-dashboard')
        form.add_error(None, 'This login route is reserved for registered users.')

    return render(request, 'app2/login.html', {
        'form': form,
        'title': 'User Login',
        'caption': 'Sign in to manage your personal App2 profile and records.',
    })


def app2_signup_view(request):
    if request.user.is_authenticated:
        return redirect('app2-dashboard')

    form = App2SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        group, _ = Group.objects.get_or_create(name='user')
        user.groups.add(group)
        login(request, user)
        messages.success(request, 'Your user account has been created successfully.')
        return redirect('app2-dashboard')

    return render(request, 'app2/signup.html', {'form': form})


def app2_hr_signup_view(request):
    if request.user.is_authenticated:
        return redirect('app2-dashboard')

    form = App2SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        group, _ = Group.objects.get_or_create(name='hr')
        user.groups.add(group)
        login(request, user)
        messages.success(request, 'HR account created successfully.')
        return redirect('app2-dashboard')

    return render(request, 'app2/hr_signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('app2-home')


def _generate_jwt(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'groups': list(user.groups.values_list('name', flat=True)),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=3600),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')


def _get_user_from_token(token):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        return None, 'Token expired.'
    except jwt.InvalidTokenError:
        return None, 'Invalid token.'

    user_id = payload.get('user_id')
    if not user_id:
        return None, 'Invalid token payload.'

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None, 'User not found.'

    return user, None


def jwt_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return JsonResponse({'detail': 'Authorization header missing or invalid.'}, status=401)

        token = auth_header.split(' ', 1)[1].strip()
        user, error = _get_user_from_token(token)
        if error:
            return JsonResponse({'detail': error}, status=401)

        request.user = user
        return view_func(request, *args, **kwargs)

    return wrapper


def api_token_view(request):
    if request.method != 'POST':
        return JsonResponse({'detail': 'POST required.'}, status=405)

    form = App2AuthenticationForm(request=request, data=request.POST)
    if not form.is_valid():
        return JsonResponse({'detail': 'Invalid credentials.'}, status=401)

    user = form.get_user()
    token = _generate_jwt(user)

    return JsonResponse({
        'access': token,
        'user': {
            'id': user.id,
            'username': user.username,
            'groups': list(user.groups.values_list('name', flat=True)),
        },
    })


@jwt_required
def api_current_user(request):
    if request.method != 'GET':
        return JsonResponse({'detail': 'GET required.'}, status=405)

    user = request.user
    return JsonResponse({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'groups': list(user.groups.values_list('name', flat=True)),
    })


@login_required
def app2_update_status(request, pk):
    if not (request.user.groups.filter(name__in=['admin', 'hr']).exists() or request.user.is_superuser):
        messages.warning(request, 'You do not have permission to update application status.')
        return redirect('app2-list')

    application = get_object_or_404(App2Data, pk=pk)
    if request.method != 'POST':
        return redirect('app2-list')

    status = request.POST.get('status')
    valid_statuses = [choice[0] for choice in STATUS_CHOICES]
    if status not in valid_statuses:
        messages.error(request, 'Invalid status selected.')
        return redirect('app2-list')

    if application.status != status:
        application.status = status
        application.save()
        messages.success(request, f'Application status updated to {status}.')

        recipient = application.user.email or application.email
        if recipient:
            subject = f'Your application status has been updated to {status}'
            message = (
                f'Hello {application.full_name or application.user.username},\n\n'
                f'Your application for {application.role} in {application.department} has been updated to "{status}".\n\n'
                'Thank you for using our application portal.\n'
                'Best regards,\nHR Team'
            )
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [recipient], fail_silently=True)
        else:
            messages.warning(request, 'No applicant email found; notification was not sent.')
    else:
        messages.info(request, 'The application status was already set to this value.')

    return redirect('app2-list')


@login_required
def dashboard(request):
    user = request.user
    staff_access = user.groups.filter(name__in=['admin', 'hr']).exists() or user.is_superuser
    if staff_access:
        employee_count = User.objects.filter(groups__name='user').count()
        item_count = App2Data.objects.count()
        return render(request, 'app2/dashboard.html', {
            'item_count': item_count,
            'employee_count': employee_count,
            'is_admin': user.groups.filter(name='admin').exists() or user.is_superuser,
            'is_hr': user.groups.filter(name='hr').exists(),
        })

    if user.groups.filter(name='user').exists():
        items = App2Data.objects.filter(user=user).order_by('-updated_at')
        return render(request, 'app2/user_dashboard.html', {
            'items': items,
        })

    messages.warning(request, 'Your account does not have App2 access. Contact an administrator.')
    return redirect('app2-home')


@login_required
def profile_view(request):
    if not request.user.groups.filter(name='user').exists():
        return redirect('app2-dashboard')

    form = UserProfileForm(request.POST or None, instance=request.user)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('app2-profile')

    return render(request, 'app2/profile.html', {'form': form})


@login_required
def apply_job_view(request):
    if not request.user.groups.filter(name='user').exists():
        messages.warning(request, 'Only candidates can submit applications.')
        return redirect('app2-dashboard')

    form = App2DataForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        application = form.save(commit=False)
        application.user = request.user
        application.save()
        messages.success(request, 'Your application has been submitted.')
        return redirect('app2-user-dashboard')

    return render(request, 'app2/form.html', {
        'form': form,
        'title': 'Apply for a Job',
    })


@login_required
def candidate_dashboard(request):
    return dashboard(request)


class App2DataListView(LoginRequiredMixin, ListView):
    model = App2Data
    template_name = 'app2/list.html'
    context_object_name = 'items'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.groups.filter(name__in=['admin', 'hr']).exists() or self.request.user.is_superuser:
            return queryset.order_by('-updated_at')
        return queryset.filter(user=self.request.user).order_by('-updated_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['can_update_status'] = self.request.user.groups.filter(name__in=['admin', 'hr']).exists() or self.request.user.is_superuser
        context['status_choices'] = STATUS_CHOICES
        return context


class App2DataCreateView(LoginRequiredMixin, CreateView):
    model = App2Data
    form_class = App2DataForm
    template_name = 'app2/form.html'
    success_url = reverse_lazy('app2-user-dashboard')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class App2DataUpdateView(LoginRequiredMixin, App2OwnerMixin, UpdateView):
    model = App2Data
    form_class = App2DataForm
    template_name = 'app2/form.html'
    success_url = reverse_lazy('app2-user-dashboard')


class App2DataDeleteView(LoginRequiredMixin, App2OwnerMixin, DeleteView):
    model = App2Data
    template_name = 'app2/confirm_delete.html'
    success_url = reverse_lazy('app2-user-dashboard')
