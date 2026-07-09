from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect

urlpatterns = [
    # path('', lambda request: redirect('accounts:login')),
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('dashboard/', include('dashboard.urls')),
    path('customers/', include('customers.urls')),
    path('tasks/', include('tasks.urls')),
    path('attendance/', include('attendance.urls')),
    path('visits/', include('visits.urls')),
    path('notifications/', include('notifications.urls')),
    path('feedbacks/', include('feedbacks.urls')),
    path('analytics/', include('analytics.urls')),
    path('leaves/', include('leaves.urls')),
    path('api/', include('api.urls')),
    path('ai/', include('ai_engine.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)