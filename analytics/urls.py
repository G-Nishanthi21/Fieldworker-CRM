from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('', views.AnalyticsView.as_view(), name='home'),
    path('export-pdf/', views.ExportPDFView.as_view(), name='export_pdf'),
]