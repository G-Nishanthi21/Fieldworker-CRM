from django.db import models
from django.conf import settings


class Customer(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    company = models.CharField(max_length=150, blank=True)

    STATUS_CHOICES = (
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('lead', 'Lead'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')

    assigned_worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='customers'
    )

    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Lead(models.Model):
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    company = models.CharField(max_length=150, blank=True)

    SOURCE_CHOICES = (
        ('walk_in', 'Walk In'),
        ('referral', 'Referral'),
        ('online', 'Online'),
        ('cold_call', 'Cold Call'),
        ('other', 'Other'),
    )
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='other')

    STATUS_CHOICES = (
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('interested', 'Interested'),
        ('not_interested', 'Not Interested'),
        ('converted', 'Converted'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='leads'
    )

    notes = models.TextField(blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    converted_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.status}"