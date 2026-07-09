from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.utils import timezone

from accounts.models import User
from visits.models import Visit
from tasks.models import Task
from attendance.models import Attendance
from customers.models import Customer


@method_decorator(login_required, name='dispatch')
class DashboardHomeView(View):

    def get(self, request):
        user = request.user

        # Admin / Manager Dashboard
        if user.is_admin or user.is_manager:
            today = timezone.now().date()

            total_workers = User.objects.filter(role='field_worker').count()
            total_managers = User.objects.filter(role='manager').count()
            on_duty_workers = User.objects.filter(role='field_worker', is_on_duty=True).count()
            recent_workers = User.objects.filter(role='field_worker').order_by('-created_at')[:5]
            total_customers = Customer.objects.count()
            total_visits = Visit.objects.count()
            pending_tasks = Task.objects.filter(status='pending').count()
            today_attendance = Attendance.objects.filter(date=today).count()
            recent_visits = Visit.objects.all()[:5]
            recent_tasks = Task.objects.all()[:5]
            pending_requests = Visit.objects.filter(status='pending')[:5]
            pending_requests_count = Visit.objects.filter(status='pending').count()

            context = {
                'total_workers': total_workers,
                'total_managers': total_managers,
                'on_duty_workers': on_duty_workers,
                'recent_workers': recent_workers,
                'total_customers': total_customers,
                'total_visits': total_visits,
                'pending_tasks': pending_tasks,
                'today_attendance': today_attendance,
                'recent_visits': recent_visits,
                'recent_tasks': recent_tasks,
                'pending_requests': pending_requests,
                'pending_requests_count': pending_requests_count,
            }
            return render(request, 'dashboard/home.html', context)

        elif user.is_field_worker:
            today = timezone.now().date()

            my_visits = Visit.objects.filter(worker=user)[:5]
            my_tasks = Task.objects.filter(assigned_to=user, status='pending')[:5]
            my_rejected_visits = Visit.objects.filter(worker=user, status='rejected')[:5]
            today_attendance = Attendance.objects.filter(worker=user, date=today).first()
            total_visits = Visit.objects.filter(worker=user).count()
            completed_visits = Visit.objects.filter(
                worker=user,
                status__in=['completed', 'approved']
            ).count()
            pending_tasks_count = Task.objects.filter(assigned_to=user, status='pending').count()
            rejected_visits_count = Visit.objects.filter(worker=user, status='rejected').count()
            pending_tasks = pending_tasks_count + rejected_visits_count
            assigned_visits = Visit.objects.filter(worker=user, status='assigned')[:5]

            context = {
                'my_visits': my_visits,
                'my_tasks': my_tasks,
                'my_rejected_visits': my_rejected_visits,
                'today_attendance': today_attendance,
                'total_visits': total_visits,
                'completed_visits': completed_visits,
                'pending_tasks': pending_tasks,
                'assigned_visits': assigned_visits,
            }
            return render(request, 'dashboard/worker_dashboard.html', context)

        elif user.is_customer_role:
            my_visits = Visit.objects.filter(customer=user)[:10]
            pending_approval = Visit.objects.filter(
                customer=user,
                status__in=['completed', 'rejected']
            ).count()

            context = {
                'my_visits': my_visits,
                'pending_approval': pending_approval,
            }
            return render(request, 'dashboard/customer_dashboard.html', context)

        else:
            return render(request, 'dashboard/home.html', {})