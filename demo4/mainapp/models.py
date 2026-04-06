from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    ROLE_ADMIN = 'ADMIN'
    ROLE_HR = 'HR'
    ROLE_USER = 'USER'

    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_HR, 'HR'),
        (ROLE_USER, 'User'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=ROLE_USER)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f'{self.user.username} ({self.get_role_display()})'


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)
    else:
        Profile.objects.get_or_create(user=instance)
