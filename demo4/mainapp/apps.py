from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import OperationalError, ProgrammingError


class MainappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'mainapp'

    def ready(self):
        from django.contrib.auth.models import Group

        def create_default_groups(sender, **kwargs):
            try:
                Group.objects.get_or_create(name='admin')
                Group.objects.get_or_create(name='hr')
                Group.objects.get_or_create(name='user')
            except (OperationalError, ProgrammingError):
                pass

        post_migrate.connect(create_default_groups, sender=self)
