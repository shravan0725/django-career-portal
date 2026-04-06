from django.contrib import admin
from .models import App2Data


@admin.register(App2Data)
class App2DataAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'department', 'role', 'status', 'updated_at')
    search_fields = ('full_name', 'user__username', 'email', 'department', 'role')
    list_filter = ('department', 'role', 'status')
