from django.contrib.auth.models import User
from django.db import models


DEPARTMENT_CLOUD = 'Cloud'
DEPARTMENT_IT = 'IT'
DEPARTMENT_NETWORKING = 'Networking'

DEPARTMENT_CHOICES = [
    (DEPARTMENT_CLOUD, 'Cloud'),
    (DEPARTMENT_IT, 'IT'),
    (DEPARTMENT_NETWORKING, 'Networking'),
]

ROLE_CHOICES = [
    ('Cloud Engineer', 'Cloud Engineer'),
    ('DevOps Engineer', 'DevOps Engineer'),
    ('Cloud Architect', 'Cloud Architect'),
    ('Software Developer', 'Software Developer'),
    ('Full Stack Developer', 'Full Stack Developer'),
    ('Data Analyst/Data Scientist', 'Data Analyst/Data Scientist'),
    ('Network Engineer', 'Network Engineer'),
    ('Network Administrator', 'Network Administrator'),
]

STATUS_PENDING = 'Pending'
STATUS_REVIEWED = 'Reviewed'
STATUS_SELECTED = 'Selected'
STATUS_REJECTED = 'Rejected'

STATUS_CHOICES = [
    (STATUS_PENDING, 'Pending'),
    (STATUS_REVIEWED, 'Reviewed'),
    (STATUS_SELECTED, 'Selected'),
    (STATUS_REJECTED, 'Rejected'),
]


class App2Data(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='applications',
        db_column='user_id',
    )
    full_name = models.CharField(max_length=200, blank=True, default='')
    email = models.EmailField(blank=True, default='')
    phone = models.CharField(max_length=30, blank=True, default='')
    department = models.CharField(
        max_length=20,
        choices=DEPARTMENT_CHOICES,
        blank=True,
        default=DEPARTMENT_IT,
    )
    role = models.CharField(
        max_length=40,
        choices=ROLE_CHOICES,
        blank=True,
        default='Software Developer',
    )
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'department', 'role')
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} applying for {self.role} in {self.department}'


