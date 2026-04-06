from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect, render


def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'mainapp/home.html')


@login_required
def dashboard(request):
    if request.user.groups.filter(name='hr').exists() or request.user.is_superuser:
        return redirect('app2-hr-dashboard')
    if request.user.groups.filter(name='user').exists():
        return redirect('app2-user-dashboard')
    return redirect('home')
