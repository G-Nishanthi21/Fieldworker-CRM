from django.core.mail import send_mail
from django.conf import settings


def send_visit_completed_email(visit):
    subject = f"Visit Completed: {visit.customer_name}"
    message = f"""
Visit Completed!

Customer: {visit.customer_name}
Worker: {visit.worker.get_full_name() or visit.worker.username}
Site: {visit.site_address}
Description: {visit.work_description}

Awaiting customer approval.
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.MANAGER_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass


def send_customer_approval_email(visit):
    if visit.status == 'approved':
        subject = f"Customer Approved: {visit.customer_name}"
        message = f"{visit.customer_name} has approved your work. Great job!"
    else:
        subject = f"Customer Rejected: {visit.customer_name}"
        message = f"{visit.customer_name} rejected the work. Feedback: {visit.customer_feedback}"

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [visit.worker.email] if visit.worker.email else [settings.MANAGER_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass


def send_lead_converted_email(lead, customer):
    subject = f"Lead Converted: {lead.name}"
    message = f"""
Lead Converted to Customer!

Name: {lead.name}
Company: {lead.company or 'N/A'}
Source: {lead.source}
Assigned to: {lead.assigned_to.get_full_name() if lead.assigned_to else 'Unassigned'}
"""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.MANAGER_EMAIL],
            fail_silently=True,
        )
    except Exception:
        pass