from django.urls import path
from . import views

app_name = 'leaves'

urlpatterns = [
    path('', views.LeaveListView.as_view(), name='list'),
    path('apply/', views.LeaveCreateView.as_view(), name='apply'),
    path('<int:pk>/approve/', views.LeaveApproveView.as_view(), name='approve'),
    path('<int:pk>/reject/', views.LeaveRejectView.as_view(), name='reject'),
]