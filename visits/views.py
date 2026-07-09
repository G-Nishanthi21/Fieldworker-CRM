from django.views.generic import ListView, CreateView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.urls import reverse
from django.utils import timezone

from accounts.models import User, UserRole
from .models import Visit
from notifications.email_utils import send_visit_completed_email, send_customer_approval_email


class VisitListView(LoginRequiredMixin, ListView):
    model = Visit
    template_name = 'visits/list.html'
    context_object_name = 'visits'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Visit.objects.all()[:50]
        if user.is_customer_role:
            return Visit.objects.filter(customer=user)
        return Visit.objects.filter(worker=user)


class CustomerRequestView(LoginRequiredMixin, CreateView):
    """Customer submits a problem + before photo. Creates a Visit with status='pending'."""
    model = Visit
    template_name = 'visits/customer_request.html'
    fields = ['category', 'problem_description', 'before_photo', 'site_address', 'customer_phone']

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_customer_role:
            messages.error(request, "Only customers can submit a service request.")
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.customer = self.request.user
        form.instance.customer_name = self.request.user.get_full_name() or self.request.user.username
        form.instance.status = 'pending'
        messages.success(self.request, "Your service request has been submitted!")
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('visits:detail', kwargs={'pk': self.object.pk})


class AdminPendingRequestsView(LoginRequiredMixin, ListView):
    """Admin sees pending AND rejected requests, ready to (re)assign to a worker."""
    model = Visit
    template_name = 'visits/pending_requests.html'
    context_object_name = 'visits'

    def dispatch(self, request, *args, **kwargs):
        if not (request.user.is_admin or request.user.is_manager):
            messages.error(request, "You don't have permission to access this page.")
            return redirect('dashboard:home')
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Visit.objects.filter(status__in=['pending', 'rejected'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        workers = User.objects.filter(role=UserRole.FIELD_WORKER)
        context['workers'] = workers

        # Build a visit_id -> [matching worker ids] map so the template can
        # highlight workers whose `skills` text mentions this visit's category.
        category_map = dict(Visit.CATEGORY_CHOICES)
        visit_worker_matches = {}
        for visit in context['visits']:
            label = category_map.get(visit.category, '').lower()
            keyword = label.replace('service', '').strip()
            matched_ids = []
            if keyword:
                for worker in workers:
                    worker_skills = (worker.skills or '').lower()
                    if keyword and keyword in worker_skills:
                        matched_ids.append(worker.id)
            visit_worker_matches[visit.id] = matched_ids
        context['visit_worker_matches'] = visit_worker_matches
        return context


class AssignWorkerView(LoginRequiredMixin, View):
    """Admin assigns a specific worker to a pending or rejected visit."""

    def post(self, request, pk):
        if not (request.user.is_admin or request.user.is_manager):
            messages.error(request, "You don't have permission to do this action.")
            return redirect('dashboard:home')

        visit = get_object_or_404(Visit, pk=pk, status__in=['pending', 'rejected'])
        worker_id = request.POST.get('worker_id')
        worker = get_object_or_404(User, pk=worker_id, role=UserRole.FIELD_WORKER)

        was_rejected = (visit.status == 'rejected')

        visit.worker = worker
        visit.assigned_by = request.user
        visit.assigned_at = timezone.now()
        visit.status = 'assigned'

        if was_rejected:
            visit.after_photo = None
            visit.work_description = ''
            visit.customer_feedback = ''
            visit.customer_rating = None
            visit.started_at = None
            visit.completed_at = None
            visit.worker_latitude = None
            visit.worker_longitude = None
            visit.worker_location_updated_at = None

        visit.save()

        messages.success(request, f"Visit {'reassigned' if was_rejected else 'assigned'} to {worker.get_full_name() or worker.username}.")
        return redirect('visits:pending_requests')


class VisitStartView(LoginRequiredMixin, View):
    """Worker starts an assigned visit (clicks 'Start Work' on their dashboard)."""

    def post(self, request, pk):
        if request.user.is_customer_role:
            messages.error(request, "You don't have permission to do this action.")
            return redirect('dashboard:home')

        visit = get_object_or_404(Visit, pk=pk, worker=request.user, status='assigned')
        visit.status = 'started'
        visit.started_at = timezone.now()
        visit.save()

        messages.success(request, "Visit started!")
        return redirect('visits:detail', pk=pk)


class VisitDetailView(LoginRequiredMixin, DetailView):
    model = Visit
    template_name = 'visits/detail.html'
    context_object_name = 'visit'


class VisitCompleteView(LoginRequiredMixin, View):
    def post(self, request, pk):
        if request.user.is_customer_role:
            messages.error(request, "You don't have permission to do this action.")
            return redirect('dashboard:home')

        visit = get_object_or_404(Visit, pk=pk, worker=request.user)

        if visit.status != 'started':
            messages.warning(request, "This visit is already completed.")
            return redirect('visits:detail', pk=pk)

        after_photo = request.FILES.get('after_photo')
        if after_photo:
            visit.after_photo = after_photo

        work_description = request.POST.get('work_description', '')
        if work_description:
            visit.work_description = work_description

        visit.status = 'completed'
        visit.completed_at = timezone.now()
        visit.save()

        send_visit_completed_email(visit)

        messages.success(request, "Visit marked as completed! Awaiting customer approval.")
        return redirect('visits:detail', pk=pk)


class CustomerApprovalView(View):
    """Public view — no login required. Customer gets a link to approve/reject."""
    template_name = 'visits/customer_approval.html'

    def get(self, request, pk):
        visit = get_object_or_404(Visit, pk=pk, status='completed')
        return render(request, self.template_name, {'visit': visit})

    def post(self, request, pk):
        visit = get_object_or_404(Visit, pk=pk, status='completed')
        action = request.POST.get('action')
        feedback = request.POST.get('feedback', '')
        rating = request.POST.get('rating')

        if action == 'approve':
            visit.status = 'approved'
            msg = "Thank you! Work has been approved."
        else:
            visit.status = 'rejected'
            msg = "Feedback recorded. Our team will follow up."

        visit.customer_feedback = feedback
        visit.customer_rating = rating or None
        visit.save()

        send_customer_approval_email(visit)

        messages.success(request, msg)
        return render(request, 'visits/approval_done.html', {'visit': visit})


class CustomerRatingView(LoginRequiredMixin, View):
    """Customer rates and approves/rejects a completed visit from their dashboard."""

    def post(self, request, pk):
        visit = get_object_or_404(Visit, pk=pk, customer=request.user)

        if visit.status not in ('completed', 'approved'):
            messages.error(request, "You can only rate completed visits.")
            return redirect('visits:detail', pk=pk)

        rating = request.POST.get('rating')
        feedback = request.POST.get('feedback', '')
        action = request.POST.get('action')

        if rating:
            visit.customer_rating = int(rating)
        if feedback:
            visit.customer_feedback = feedback
        if action == 'approve':
            visit.status = 'approved'
        elif action == 'reject':
            visit.status = 'rejected'

        visit.save()
        messages.success(request, "Thank you for your feedback!")
        return redirect('visits:detail', pk=pk)


class UpdateWorkerLocationView(LoginRequiredMixin, View):
    """Worker submits their current latitude/longitude via a plain HTML form."""

    def post(self, request, pk):
        if request.user.is_customer_role:
            messages.error(request, "You don't have permission to do this action.")
            return redirect('dashboard:home')

        visit = get_object_or_404(Visit, pk=pk, worker=request.user)

        lat = request.POST.get('latitude')
        lng = request.POST.get('longitude')

        if lat and lng:
            try:
                visit.worker_latitude = float(lat)
                visit.worker_longitude = float(lng)
                visit.worker_location_updated_at = timezone.now()
                visit.save()
                messages.success(request, "Location saved!")
            except ValueError:
                messages.error(request, "Invalid latitude/longitude.")
        else:
            messages.error(request, "Please enter both latitude and longitude.")

        return redirect('visits:detail', pk=pk)
    
class AddCommentView(LoginRequiredMixin, View):
    def post(self, request, pk):
        visit = get_object_or_404(Visit, pk=pk)
        text = request.POST.get('comment', '').strip()
        if text:
            from .models import VisitComment
            VisitComment.objects.create(
                visit=visit,
                author=request.user,
                text=text
            )
            messages.success(request, "Comment added.")
        return redirect('visits:detail', pk=pk)