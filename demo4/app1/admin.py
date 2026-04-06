from django.contrib import admin
from .models import App1Data, App1Login


@admin.register(App1Data)
class App1DataAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'updated_at')
    search_fields = ('title', 'user__username')


@admin.register(App1Login)
class App1LoginAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'username', 'created_at')
    search_fields = ('user_id', 'username')
