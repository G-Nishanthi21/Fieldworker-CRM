from django.urls import path
from . import views

app_name = 'api'

urlpatterns = [
    path('login/', views.LoginAPIView.as_view(), name='login'),
    path('dashboard/', views.DashboardAPIView.as_view(), name='dashboard'),
    path('customers/', views.CustomerListAPIView.as_view(), name='customers'),
    path('customers/<int:pk>/', views.CustomerDetailAPIView.as_view(), name='customer_detail'),
    path('leads/', views.LeadListAPIView.as_view(), name='leads'),
    path('visits/', views.VisitListAPIView.as_view(), name='visits'),
    path('visits/<int:pk>/', views.VisitDetailAPIView.as_view(), name='visit_detail'),
    path('tasks/', views.TaskListAPIView.as_view(), name='tasks'),
    path('attendance/', views.AttendanceListAPIView.as_view(), name='attendance'),
]