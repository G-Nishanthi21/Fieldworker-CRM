from django.views.generic import ListView, CreateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from django.urls import reverse_lazy
from django.utils import timezone

from .models import Leave


class LeaveListView(LoginRequiredMixin, ListView):
    model = Leave
    template_name = 'leaves/list.html'
    context_object_name = 'leaves'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Leave.objects.all()
        return Leave.objects.filter(worker=user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pending_count'] = Leave.objects.filter(status='pending').count()
        context['approved_count'] = Leave.objects.filter(status='approved').count()
        context['rejected_count'] = Leave.objects.filter(status='rejected').count()
        return context


class LeaveCreateView(LoginRequiredMixin, CreateView):
    model = Leave
    template_name = 'leaves/form.html'
    fields = ['leave_type', 'from_date', 'to_date', 'reason']
    success_url = reverse_lazy('leaves:list')

    def form_valid(self, form):
        form.instance.worker = self.request.user
        messages.success(self.request, "Leave request submitted!")
        return super().form_valid(form)


class LeaveApproveView(LoginRequiredMixin, View):
    def post(self, request, pk):
        leave = get_object_or_404(Leave, pk=pk)
        leave.status = 'approved'
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.save()
        messages.success(request, f"{leave.worker.get_full_name()} leave approved!")
        return redirect('leaves:list')


class LeaveRejectView(LoginRequiredMixin, View):
    def post(self, request, pk):
        leave = get_object_or_404(Leave, pk=pk)
        leave.status = 'rejected'
        leave.reviewed_by = request.user
        leave.reviewed_at = timezone.now()
        leave.reject_reason = request.POST.get('reject_reason', '')
        leave.save()
        messages.success(request, f"{leave.worker.get_full_name()} leave rejected!")
        return redirect('leaves:list')