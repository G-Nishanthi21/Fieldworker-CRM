from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRole(models.TextChoices):
    ADMIN = 'admin', _('Admin')
    MANAGER = 'manager', _('Manager')
    FIELD_WORKER = 'field_worker', _('Field Worker')
    CUSTOMER = 'customer', _('Customer')


class User(AbstractUser):
    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.FIELD_WORKER,
    )
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        null=True,
        blank=True,
    )
    phone_number = models.CharField(
        max_length=15,
        null=True,
        blank=True,
    )
    address = models.TextField(
        null=True,
        blank=True,
    )
    current_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    current_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
    )
    last_location_update = models.DateTimeField(
        null=True,
        blank=True,
    )
    is_on_duty = models.BooleanField(default=False)
    employee_id = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        unique=True,
    )
    department = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    skills = models.TextField(
        null=True,
        blank=True,
    )
    ai_lead_score = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"

    @property
    def is_admin(self):
        return self.role == UserRole.ADMIN

    @property
    def is_manager(self):
        return self.role == UserRole.MANAGER

    @property
    def is_field_worker(self):
        return self.role == UserRole.FIELD_WORKER

    @property
    def is_customer_role(self):
        return self.role == UserRole.CUSTOMER

    def get_profile_photo_url(self):
        if self.profile_photo:
            return self.profile_photo.url
        return '/static/images/default_avatar.png'


class UserProfile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    emergency_contact = models.CharField(
        max_length=15,
        null=True,
        blank=True,
    )
    total_tasks_completed = models.IntegerField(default=0)
    performance_score = models.FloatField(default=0.0)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"Profile of {self.user.get_full_name()}"