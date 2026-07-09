from django.urls import path
from . import views

app_name = 'visits'

urlpatterns = [
    path('', views.VisitListView.as_view(), name='list'),
    path('request/', views.CustomerRequestView.as_view(), name='customer_request'),
    path('pending/', views.AdminPendingRequestsView.as_view(), name='pending_requests'),
    path('<int:pk>/assign/', views.AssignWorkerView.as_view(), name='assign_worker'),
    path('<int:pk>/start/', views.VisitStartView.as_view(), name='start'),
    path('<int:pk>/', views.VisitDetailView.as_view(), name='detail'),
    path('<int:pk>/complete/', views.VisitCompleteView.as_view(), name='complete'),
    path('<int:pk>/approval/', views.CustomerApprovalView.as_view(), name='customer_approval'),
    path('<int:pk>/rate/', views.CustomerRatingView.as_view(), name='rate'),
    path('<int:pk>/update-location/', views.UpdateWorkerLocationView.as_view(), name='update_location'),
    path('<int:pk>/comment/', views.AddCommentView.as_view(), name='add_comment'),
]