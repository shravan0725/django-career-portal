from django.urls import path
from . import views

urlpatterns = [
    path('', views.App1DataListView.as_view(), name='app1-list'),
    path('create/', views.App1DataCreateView.as_view(), name='app1-create'),
    path('<int:pk>/edit/', views.App1DataUpdateView.as_view(), name='app1-update'),
    path('<int:pk>/delete/', views.App1DataDeleteView.as_view(), name='app1-delete'),
    path('login/', views.app1_login_view, name='app1-login'),
    path('signup/', views.app1_signup_view, name='app1-signup'),
]
