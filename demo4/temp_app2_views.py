import datetime

import jwt
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CandidateAuthenticationForm, CandidateSignupForm, HRAuthenticationForm, JobApplicationForm
from .models import App2Data, DEPARTMENT_CHOICES, ROLE_CHOICES, STATUS_CHOICES

JWT_ALGORITHM = 'HS256'
JWT_EXPIRATION_SECONDS = 3600


def _generate_jwt(user):
    payload = {
        'user_id': user.id,
        'username': user.username,
        'role': 'hr' if user.groups.filter(name='hr').exists() else 'user',
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=JWT_EXPIRATION_SECONDS),
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm=JWT_ALGORITHM)
    return token


def app2_home(request):
    return render(request, 'app2/home.html')


def candidate_signup_view(request):
    if request.user.is_authenticated:
        return redirect('app2-user-dashboard' if request.user.groups.filter(name='user').exists() else 'app2-hr-dashboard')

    form = CandidateSignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        group, _ = Group.objects.get_or_create(name='user')
        user.groups.add(group)
        login(request, user)
        messages.success(request, 'Candidate account created successfully. You can now submit a job application.')
        return redirect('app2-apply')

    return render(request, 'app2/signup.html', {
        'form': form,
        'title': 'Candidate Signup',
        'caption': 'Register as a candidate to submit job applications and view your submissions.',
    })


def candidate_login_view(request):
    if request.user.is_authenticated:
        return redirect('app2-user-dashboard')

    form = CandidateAuthenticationForm(request=request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user.groups.filter(name='user').exists():
            login(request, user)
            return redirect('app2-user-dashboard')
        form.add_error(None, 'Please use the HR login if you are an HR user.')

    return render(request, 'app2/login.html', {
        'form': form,
        'title': 'Candidate Login',
        'caption': 'Sign in to submit your job application and track application status.',
    })


def hr_signup_view(request):
    if request.user.is_authenticated:
        return redirect('app2-hr-dashboard')

    form = CandidateSignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        group, _ = Group.objects.get_or_create(name='hr')
        user.groups.add(group)
        login(request, user)
        messages.success(request, 'HR account created successfully. You can now access the HR dashboard.')
        return redirect('app2-hr-dashboard')

    return render(request, 'app2/hr_signup.html', {
        'form': form,
        'title': 'HR Signup',
        'caption': 'Create an HR account to review candidate applications and manage hiring.',
    })


def hr_login_view(request):
    if request.user.is_authenticated:
        return redirect('app2-hr-dashboard')

    form = HRAuthenticationForm(request=request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        if user.groups.filter(name='hr').exists():
            login(request, user)
            return redirect('app2-hr-dashboard')
        form.add_error(None, 'This login route is reserved for HR users.')

    return render(request, 'app2/login.html', {
        'form': form,
        'title': 'HR Login',
        'caption': 'HR users can inspect candidate applications, filter by role or department, and update statuses.',
    })


def logout_view(request):
    logout(request)
    return redirect('app2-home')


@login_required
def apply_job_view(request):
    if not request.user.groups.filter(name='user').exists():
        return redirect('app2-home')

    initial = {
        'full_name': request.user.get_full_name() or request.user.username,
        'email': request.user.email,
    }
    form = JobApplicationForm(request.POST or None, request.FILES or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        application = form.save(commit=False)
        application.candidate = request.user
        duplicate = App2Data.objects.filter(
            candidate=request.user,
            department=application.department,
            role=application.role,
        ).exists()
        if duplicate:
            form.add_error(None, 'You have already submitted an application for this department and role.')
        else:
            application.save()
            messages.success(request, 'Your job application has been submitted successfully.')
            return redirect('app2-user-dashboard')

    return render(request, 'app2/form.html', {
        'form': form,
        'title': 'Job Application',
        'caption': 'Submit your candidate profile, upload your resume, and choose the department and role you are applying for.',
        'departments': DEPARTMENT_CHOICES,
        'roles': ROLE_CHOICES,
    })


@login_required
def candidate_dashboard(request):
    if not request.user.groups.filter(name='user').exists():
        return redirect('app2-home')

    applications = App2Data.objects.filter(candidate=request.user)
    return render(request, 'app2/user_dashboard.html', {
        'applications': applications,
    })


@login_required
def hr_dashboard(request):
    if not request.user.groups.filter(name='hr').exists():
        return redirect('app2-home')

    applications = App2Data.objects.all()
    department = request.GET.get('department')
    role = request.GET.get('role')
    search = request.GET.get('search')

    if department:
        applications = applications.filter(department=department)
    if role:
        applications = applications.filter(role=role)
    if search:
        applications = applications.filter(full_name__icontains=search) | applications.filter(email__icontains=search)

    return render(request, 'app2/dashboard.html', {
        'applications': applications,
        'departments': DEPARTMENT_CHOICES,
        'roles': ROLE_CHOICES,
        'selected_department': department,
        'selected_role': role,
        'search': search,
        'status_choices': STATUS_CHOICES,
    })


@login_required
def hr_application_detail(request, pk):
    if not request.user.groups.filter(name='hr').exists():
        return redirect('app2-home')

    application = get_object_or_404(App2Data, pk=pk)
    if request.method == 'POST':
        selected_status = request.POST.get('status')
        valid_statuses = {choice[0] for choice in STATUS_CHOICES}
        if selected_status in valid_statuses:
            application.status = selected_status
            application.save()
            messages.success(request, 'Application status updated.')
            return redirect('app2-hr-application-detail', pk=pk)

    return render(request, 'app2/application_detail.html', {
        'application': application,
        'status_choices': STATUS_CHOICES,
    })
