from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='app2-home'),
    path('signup/', views.app2_signup_view, name='app2-signup'),
    path('login/', views.app2_login_view, name='app2-login'),
    path('logout/', views.logout_view, name='app2-logout'),
    path('hr/signup/', views.app2_hr_signup_view, name='app2-hr-signup'),
    path('hr/login/', views.hr_login_view, name='app2-hr-login'),
    path('api/token/', views.api_token_view, name='app2-api-token'),
    path('api/me/', views.api_current_user, name='app2-api-current-user'),
    path('dashboard/', views.dashboard, name='app2-dashboard'),
    path('hr/dashboard/', views.dashboard, name='app2-hr-dashboard'),
    path('applications/', views.App2DataListView.as_view(), name='app2-list'),
    path('create/', views.App2DataCreateView.as_view(), name='app2-create'),
    path('application/<int:pk>/status/', views.app2_update_status, name='app2-update-status'),
    path('application/<int:pk>/edit/', views.App2DataUpdateView.as_view(), name='app2-edit'),
    path('application/<int:pk>/delete/', views.App2DataDeleteView.as_view(), name='app2-delete'),
    path('apply/', views.apply_job_view, name='app2-apply'),
    path('profile/', views.profile_view, name='app2-profile'),
    path('my-applications/', views.candidate_dashboard, name='app2-user-dashboard'),
]
