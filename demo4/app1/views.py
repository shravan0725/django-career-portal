from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import Group, User
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .forms import App1AuthenticationForm, App1DataForm, App1SignupForm
from .models import App1Data, App1Login


class App1OwnerMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return self.request.user == obj.user or self.request.user.groups.filter(name='admin').exists() or self.request.user.is_superuser

    def handle_no_permission(self):
        return super().handle_no_permission()


def app1_login_view(request):
    if request.user.is_authenticated:
        return redirect('app1-list')

    form = App1AuthenticationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('app1-list')

    return render(request, 'app1/login.html', {'form': form})


def app1_signup_view(request):
    if request.user.is_authenticated:
        return redirect('app1-list')

    form = App1SignupForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        group, _ = Group.objects.get_or_create(name='user')
        user.groups.add(group)
        App1Login.objects.create(
            user_id=form.cleaned_data['user_id'],
            username=user.username,
            password=make_password(form.cleaned_data['password1']),
        )
        login(request, user)
        return redirect('app1-list')

    return render(request, 'app1/signup.html', {'form': form})


class App1DataListView(LoginRequiredMixin, ListView):
    model = App1Data
    template_name = 'app1/list.html'
    context_object_name = 'items'

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.request.user.groups.filter(name='admin').exists() or self.request.user.is_superuser:
            return queryset.order_by('-updated_at')
        return queryset.filter(user=self.request.user).order_by('-updated_at')


class App1DataCreateView(LoginRequiredMixin, CreateView):
    model = App1Data
    form_class = App1DataForm
    template_name = 'app1/form.html'
    success_url = reverse_lazy('app1-list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


class App1DataUpdateView(LoginRequiredMixin, App1OwnerMixin, UpdateView):
    model = App1Data
    form_class = App1DataForm
    template_name = 'app1/form.html'
    success_url = reverse_lazy('app1-list')


class App1DataDeleteView(LoginRequiredMixin, App1OwnerMixin, DeleteView):
    model = App1Data
    template_name = 'app1/confirm_delete.html'
    success_url = reverse_lazy('app1-list')
