from django.views.generic import TemplateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponse

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from attendance.models import Attendance
from visits.models import Visit
from tasks.models import Task
from customers.models import Customer


class AnalyticsView(LoginRequiredMixin, TemplateView):
    template_name = 'analytics/list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = timezone.now().date()
        last_30 = today - timedelta(days=30)

        # Attendance
        context['total_checkins'] = Attendance.objects.filter(date__gte=last_30).count()
        context['today_checkins'] = Attendance.objects.filter(date=today).count()

        # Visits
        total_visits = Visit.objects.filter(started_at__date__gte=last_30).count()
        completed_visits = Visit.objects.filter(started_at__date__gte=last_30, status='completed').count()
        approved_visits = Visit.objects.filter(started_at__date__gte=last_30, status='approved').count()
        pending_visits = Visit.objects.filter(started_at__date__gte=last_30, status='started').count()

        context['total_visits'] = total_visits
        context['completed_visits'] = completed_visits
        context['approved_visits'] = approved_visits
        context['pending_visits'] = pending_visits

        context['completed_visits_pct'] = int((completed_visits / total_visits * 100) if total_visits else 0)
        context['approved_visits_pct'] = int((approved_visits / total_visits * 100) if total_visits else 0)
        context['pending_visits_pct'] = int((pending_visits / total_visits * 100) if total_visits else 0)

        # Tasks
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status='completed').count()
        inprogress_tasks = Task.objects.filter(status='in_progress').count()
        pending_tasks = Task.objects.filter(status='pending').count()

        context['total_tasks'] = total_tasks
        context['completed_tasks'] = completed_tasks
        context['inprogress_tasks'] = inprogress_tasks
        context['pending_tasks'] = pending_tasks

        context['completed_tasks_pct'] = int((completed_tasks / total_tasks * 100) if total_tasks else 0)
        context['inprogress_tasks_pct'] = int((inprogress_tasks / total_tasks * 100) if total_tasks else 0)
        context['pending_tasks_pct'] = int((pending_tasks / total_tasks * 100) if total_tasks else 0)

        # Customers
        total_customers = Customer.objects.count()
        context['total_customers'] = total_customers
        context['active_customers'] = Customer.objects.filter(status='active').count()
        context['lead_customers'] = Customer.objects.filter(status='lead').count()

        # Last 7 days attendance
        attendance_zip = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            count = Attendance.objects.filter(date=day).count()
            attendance_zip.append({'label': day.strftime('%d %b'), 'count': count})
        context['attendance_zip'] = attendance_zip

        return context


class ExportPDFView(LoginRequiredMixin, View):
    def get(self, request):
        today = timezone.now().date()
        last_30 = today - timedelta(days=30)

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="FieldCRM_Report_{today}.pdf"'

        doc = SimpleDocTemplate(response, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("FieldCRM — Performance Report", styles['Title']))
        elements.append(Paragraph(f"Generated on: {today.strftime('%d %B %Y')}", styles['Normal']))
        elements.append(Spacer(1, 20))

        total_visits = Visit.objects.filter(started_at__date__gte=last_30).count()
        completed_visits = Visit.objects.filter(started_at__date__gte=last_30, status='completed').count()
        approved_visits = Visit.objects.filter(started_at__date__gte=last_30, status='approved').count()
        total_tasks = Task.objects.count()
        completed_tasks = Task.objects.filter(status='completed').count()
        total_checkins = Attendance.objects.filter(date__gte=last_30).count()
        total_customers = Customer.objects.count()

        elements.append(Paragraph("Summary (Last 30 Days)", styles['Heading2']))
        summary_data = [
            ['Metric', 'Count'],
            ['Total Customers', str(total_customers)],
            ['Total Visits', str(total_visits)],
            ['Completed Visits', str(completed_visits)],
            ['Customer Approved Visits', str(approved_visits)],
            ['Total Tasks', str(total_tasks)],
            ['Completed Tasks', str(completed_tasks)],
            ['Attendance Check-ins', str(total_checkins)],
        ]
        summary_table = Table(summary_data, colWidths=[10*cm, 5*cm])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 25))

        elements.append(Paragraph("Recent Visits", styles['Heading2']))
        visits = Visit.objects.all()[:15]
        visit_data = [['Customer', 'Worker', 'Status', 'Date']]
        for v in visits:
            visit_data.append([
                v.customer_name,
                v.worker.get_full_name() or v.worker.username,
                v.get_status_display(),
                v.started_at.strftime('%d %b %Y')
            ])
        visit_table = Table(visit_data, colWidths=[5*cm, 4*cm, 3*cm, 3*cm])
        visit_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(visit_table)
        elements.append(Spacer(1, 25))

        elements.append(Paragraph("Recent Tasks", styles['Heading2']))
        tasks = Task.objects.all()[:15]
        task_data = [['Title', 'Assigned To', 'Priority', 'Status']]
        for t in tasks:
            task_data.append([
                t.title,
                t.assigned_to.get_full_name() or t.assigned_to.username,
                t.get_priority_display(),
                t.get_status_display()
            ])
        task_table = Table(task_data, colWidths=[5*cm, 4*cm, 3*cm, 3*cm])
        task_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ('FONTSIZE', (0, 0), (-1, -1), 9),
            ('TOPPADDING', (0, 0), (-1, -1), 6),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ]))
        elements.append(task_table)

        doc.build(elements)
        return response