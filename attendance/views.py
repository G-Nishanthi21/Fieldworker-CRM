from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse

from .models import Attendance


class AttendanceListView(LoginRequiredMixin, TemplateView):
    template_name = 'attendance/list.html'

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_customer_role:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()

        context['today_attendance'] = Attendance.objects.filter(
            worker=self.request.user, date=today
        ).first()

        if self.request.user.is_admin or self.request.user.is_manager:
            context['attendance_list'] = Attendance.objects.all()[:50]
        else:
            context['attendance_list'] = Attendance.objects.filter(
                worker=self.request.user
            )[:30]

        return context


class CheckInView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_customer_role:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard:home')

        today = timezone.now().date()

        existing = Attendance.objects.filter(worker=request.user, date=today).first()
        if existing:
            messages.warning(request, "You have already checked in today.")
            return redirect('attendance:list')

        Attendance.objects.create(
            worker=request.user,
            check_in_address='Office',
        )

        messages.success(request, "Checked in successfully!")
        return redirect('attendance:list')


class CheckOutView(LoginRequiredMixin, View):
    def get(self, request):
        if request.user.is_customer_role:
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard:home')

        today = timezone.now().date()

        attendance = get_object_or_404(
            Attendance, worker=request.user, date=today
        )

        if attendance.check_out_time:
            messages.warning(request, "You have already checked out today.")
            return redirect('attendance:list')

        attendance.check_out_time = timezone.now()
        attendance.check_out_address = 'Office'
        attendance.save()

        messages.success(request, "Checked out successfully!")
        return redirect('attendance:list')