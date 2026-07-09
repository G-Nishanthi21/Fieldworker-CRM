from django.db import models
from django.conf import settings


class Visit(models.Model):
    # Who submitted the original service request (the customer)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_requests'
    )

    # Who assigned this work to a worker (the admin/manager)
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_visits'
    )

    # The worker doing the job — empty until admin assigns it
    worker = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='visits',
        null=True,
        blank=True
    )

    customer_name = models.CharField(max_length=150)
    customer_phone = models.CharField(max_length=20, blank=True)
    site_address = models.CharField(max_length=255, blank=True)

    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)

    # Worker's live location (updated when worker shares location during a visit)
    worker_latitude = models.FloatField(null=True, blank=True)
    worker_longitude = models.FloatField(null=True, blank=True)
    worker_location_updated_at = models.DateTimeField(null=True, blank=True)

    # Type of service requested — used to suggest a matching worker by skill
    CATEGORY_CHOICES = (
        ('ac_repair', 'AC Repair'),
        ('electrical', 'Electrical'),
        ('plumbing', 'Plumbing'),
        ('carpentry', 'Carpentry'),
        ('painting', 'Painting'),
        ('general', 'General Service'),
    )
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')

    # Customer's problem description + before photo (submitted by customer)
    problem_description = models.TextField(blank=True)
    before_photo = models.ImageField(upload_to='visits/before/', null=True, blank=True)

    # Worker's notes + after photo (submitted by worker on completion)
    work_description = models.TextField(blank=True)
    after_photo = models.ImageField(upload_to='visits/after/', null=True, blank=True)

    STATUS_CHOICES = (
        ('pending', 'Pending — Awaiting Assignment'),
        ('assigned', 'Assigned to Worker'),
        ('started', 'Started'),
        ('completed', 'Completed'),
        ('approved', 'Approved by Customer'),
        ('rejected', 'Rejected by Customer'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    customer_feedback = models.TextField(blank=True)
    customer_rating = models.PositiveSmallIntegerField(null=True, blank=True)

    requested_at = models.DateTimeField(auto_now_add=True)
    assigned_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-requested_at']

    def __str__(self):
        return f"{self.customer_name} - {self.status}"
    
class VisitComment(models.Model):
    visit = models.ForeignKey(
        Visit,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on Visit {self.visit.id}"