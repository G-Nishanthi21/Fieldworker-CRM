from django.urls import path
from . import views

app_name = 'customers'

urlpatterns = [
    path('', views.CustomerListView.as_view(), name='list'),
    path('add/', views.CustomerCreateView.as_view(), name='add'),
    path('<int:pk>/edit/', views.CustomerUpdateView.as_view(), name='edit'),
    path('<int:pk>/delete/', views.CustomerDeleteView.as_view(), name='delete'),

    # Leads
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/add/', views.LeadCreateView.as_view(), name='lead_add'),
    path('leads/<int:pk>/edit/', views.LeadUpdateView.as_view(), name='lead_edit'),
    path('leads/<int:pk>/convert/', views.LeadConvertView.as_view(), name='lead_convert'),
    path('<int:customer_id>/leads/add/', views.LeadCreateView.as_view(), name='lead_add'),
]