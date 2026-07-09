import json
import urllib.request
import urllib.error
from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.contrib import messages
from django.utils import timezone

from .models import Notification
from attendance.models import Attendance
from visits.models import Visit

ANTHROPIC_API_KEY = "sk-ant-api03-xxxxxxxxxx..."  # Replace with your actual key


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/list.html'
    context_object_name = 'notifications'

    def get_queryset(self):
        user = self.request.user
        if user.is_admin or user.is_manager:
            return Notification.objects.all()[:50]
        return Notification.objects.filter(recipient=user)[:30]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['unread_count'] = Notification.objects.filter(
            recipient=self.request.user, is_read=False
        ).count()
        return context


class MarkReadView(LoginRequiredMixin, View):
    def post(self, request, pk):
        notif = Notification.objects.filter(pk=pk, recipient=request.user).first()
        if notif:
            notif.is_read = True
            notif.save()
        return redirect('notifications:list')


class GenerateAINotificationView(LoginRequiredMixin, View):
    def post(self, request):
        today = timezone.now().date()

        checked_in_today = Attendance.objects.filter(date=today).count()
        visits_today = Visit.objects.filter(started_at__date=today).count()
        completed_visits = Visit.objects.filter(started_at__date=today, status='completed').count()
        pending_visits = Visit.objects.filter(started_at__date=today, status='started').count()

        prompt = f"""You are an AI assistant for a Field Worker CRM system.

Today's summary:
- Workers checked in: {checked_in_today}
- Total visits started: {visits_today}
- Completed visits: {completed_visits}
- Pending visits: {pending_visits}
- Date: {today}

Generate 3 short, actionable manager notifications based on this data.
Respond ONLY with a JSON array like this:
[
  {{"title": "...", "message": "...", "type": "info"}},
  {{"title": "...", "message": "...", "type": "warning"}},
  {{"title": "...", "message": "...", "type": "success"}}
]
Types can be: info, warning, success, danger.
Keep each message under 100 words. No extra text outside the JSON."""

        try:
            payload = json.dumps({
                "model": "claude-sonnet-4-6",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": prompt}]
            }).encode('utf-8')

            req = urllib.request.Request(
                "https://api.anthropic.com/v1/messages",
                data=payload,
                headers={
                    "Content-Type": "application/json",
                    "x-api-key": ANTHROPIC_API_KEY,
                    "anthropic-version": "2023-06-01"
                },
                method="POST"
            )

            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode('utf-8'))

            ai_text = data['content'][0]['text']

            # Clean JSON if wrapped in backticks
            ai_text = ai_text.strip()
            if ai_text.startswith("```"):
                ai_text = ai_text.split("```")[1]
                if ai_text.startswith("json"):
                    ai_text = ai_text[4:]

            notifications_data = json.loads(ai_text.strip())

            for notif in notifications_data:
                Notification.objects.create(
                    recipient=request.user,
                    title=notif.get('title', 'AI Alert'),
                    message=notif.get('message', ''),
                    notif_type=notif.get('type', 'info'),
                    is_ai_generated=True
                )

            messages.success(request, f"✅ AI generated {len(notifications_data)} notifications!")

        except Exception as e:
            messages.error(request, f"AI Error: {str(e)}")

        return redirect('notifications:list')
    
class GenerateAINotificationView(LoginRequiredMixin, View):
    def post(self, request):
        today = timezone.now().date()

        checked_in_today = Attendance.objects.filter(date=today).count()
        visits_today = Visit.objects.filter(started_at__date=today).count()
        completed_visits = Visit.objects.filter(started_at__date=today, status='completed').count()
        pending_visits = Visit.objects.filter(started_at__date=today, status='started').count()

        # Smart rule-based notifications (no API needed!)
        notifications_data = []

        # Attendance alert
        if checked_in_today == 0:
            notifications_data.append({
                'title': '⚠️ No Workers Checked In Today',
                'message': f'No field workers have checked in today ({today}). Please follow up with your team immediately.',
                'type': 'danger'
            })
        else:
            notifications_data.append({
                'title': f'✅ {checked_in_today} Worker(s) Active Today',
                'message': f'{checked_in_today} field worker(s) have checked in today. Team is on duty and ready for assignments.',
                'type': 'success'
            })

        # Visit progress alert
        if pending_visits > 0:
            notifications_data.append({
                'title': f'🔄 {pending_visits} Visit(s) In Progress',
                'message': f'{pending_visits} visit(s) are currently in progress. Monitor completion status and ensure workers submit after-photos.',
                'type': 'warning'
            })

        if completed_visits > 0:
            notifications_data.append({
                'title': f'🎯 {completed_visits} Visit(s) Completed Today',
                'message': f'Great progress! {completed_visits} out of {visits_today} visits completed today. Check customer approval status.',
                'type': 'success'
            })

        # Daily summary
        notifications_data.append({
            'title': f'📊 Daily Summary — {today}',
            'message': f'Today: {checked_in_today} workers active, {visits_today} visits started, {completed_visits} completed, {pending_visits} pending.',
            'type': 'info'
        })

        # Save to database
        count = 0
        for notif in notifications_data:
            Notification.objects.create(
                recipient=request.user,
                title=notif['title'],
                message=notif['message'],
                notif_type=notif['type'],
                is_ai_generated=True
            )
            count += 1

        messages.success(request, f"✅ {count} smart notifications generated!")
        return redirect('notifications:list')