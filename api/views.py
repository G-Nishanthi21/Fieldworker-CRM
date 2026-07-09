from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from customers.models import Customer, Lead
from visits.models import Visit
from tasks.models import Task
from attendance.models import Attendance

from .serializers import (
    UserSerializer, CustomerSerializer, LeadSerializer,
    VisitSerializer, TaskSerializer, AttendanceSerializer,
)

User = get_user_model()


class LoginAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            token, _ = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'user': UserSerializer(user).data
            })
        return Response({'error': 'Invalid credentials'}, status=400)


class CustomerListAPIView(generics.ListCreateAPIView):
    serializer_class = CustomerSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Customer.objects.all()
        return Customer.objects.filter(assigned_worker=user)


class CustomerDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CustomerSerializer
    queryset = Customer.objects.all()


class LeadListAPIView(generics.ListCreateAPIView):
    serializer_class = LeadSerializer
    queryset = Lead.objects.all()


class VisitListAPIView(generics.ListCreateAPIView):
    serializer_class = VisitSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Visit.objects.all()
        return Visit.objects.filter(worker=user)


class VisitDetailAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = VisitSerializer
    queryset = Visit.objects.all()


class TaskListAPIView(generics.ListCreateAPIView):
    serializer_class = TaskSerializer
    queryset = Task.objects.all()


class AttendanceListAPIView(generics.ListCreateAPIView):
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Attendance.objects.all()
        return Attendance.objects.filter(worker=user)


class DashboardAPIView(APIView):
    def get(self, request):
        from django.utils import timezone
        from datetime import timedelta
        today = timezone.now().date()

        return Response({
            'total_customers': Customer.objects.count(),
            'total_visits': Visit.objects.count(),
            'pending_tasks': Task.objects.filter(status='pending').count(),
            'today_attendance': Attendance.objects.filter(date=today).count(),
        })