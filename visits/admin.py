from django.contrib import admin
from .models import Visit


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer_id', 'customer', 'site_address', 'status', 'worker')
    list_filter = ('status',)
    search_fields = ('site_address',)