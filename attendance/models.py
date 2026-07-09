from django.db import models
from django.conf import settings


class Attendance(models.Model):
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='attendances'
    )

    # Check-in details
    check_in_time = models.DateTimeField(auto_now_add=True)
    check_in_latitude = models.FloatField(null=True, blank=True)
    check_in_longitude = models.FloatField(null=True, blank=True)
    check_in_address = models.CharField(max_length=255, blank=True)

    # Check-out details
    check_out_time = models.DateTimeField(null=True, blank=True)
    check_out_latitude = models.FloatField(null=True, blank=True)
    check_out_longitude = models.FloatField(null=True, blank=True)
    check_out_address = models.CharField(max_length=255, blank=True)

    date = models.DateField(auto_now_add=True)

    STATUS_CHOICES = (
        ('present', 'Present'),
        ('half_day', 'Half Day'),
        ('absent', 'Absent'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present')

    class Meta:
        ordering = ['-date', '-check_in_time']

    def __str__(self):
        return