"""
Email Notification Service for EduEvent.
Sends SMTP emails on key events using Django templates.
"""
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

logger = logging.getLogger(__name__)


def _send(subject, template_name, context, recipient_list):
    """Internal sender with error handling."""
    if not recipient_list:
        return

    context.setdefault('college_name', settings.COLLEGE_NAME)
    context.setdefault('site_url', settings.SITE_URL)

    try:
        html_message = render_to_string(f'email/{template_name}.html', context)
        plain_message = strip_tags(html_message)

        send_mail(
            subject=f"[EduEvent] {subject}",
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=True,
        )
        logger.info(f"Email sent: '{subject}' to {recipient_list}")
    except Exception as e:
        logger.error(f"Email send error: {e}")


def notify_new_event_request(event):
    """Notify admin(s) about a new event request from HOD."""
    from core.models import UserProfile
    admins = UserProfile.objects.filter(role='admin', is_active=True, email_notifications=True)
    emails = list(admins.values_list('email', flat=True))

    _send(
        subject=f"New Event Request: {event.title}",
        template_name='new_event',
        context={
            'event': event,
            'hod_name': event.hod.name if event.hod else 'Unknown',
        },
        recipient_list=emails,
    )

def notify_new_user_registration(user_profile):
    """Notify admin(s) about a new user registration that needs approval."""
    from core.models import UserProfile
    admins = UserProfile.objects.filter(role='admin', is_active=True, email_notifications=True)
    emails = list(admins.values_list('email', flat=True))

    _send(
        subject=f"New Registration Approval Required: {user_profile.name} ({user_profile.role.capitalize()})",
        template_name='new_user_registration',
        context={
            'user': user_profile,
        },
        recipient_list=emails,
    )


def notify_event_approved(event):
    """Notify HOD and relevant students that an event was approved."""
    recipients = []
    if event.hod and event.hod.email_notifications:
        recipients.append(event.hod.email)

    # Also notify students of the branch
    from core.models import UserProfile
    students = UserProfile.objects.filter(
        role='student', branch=event.branch,
        is_active=True, is_approved=True, email_notifications=True
    )
    recipients.extend(students.values_list('email', flat=True))

    _send(
        subject=f"Event Approved: {event.title}",
        template_name='event_approved',
        context={'event': event},
        recipient_list=list(set(recipients)),
    )


def notify_event_rejected(event):
    """Notify HOD that an event was rejected."""
    if event.hod and event.hod.email_notifications:
        _send(
            subject=f"Event Rejected: {event.title}",
            template_name='event_rejected',
            context={'event': event},
            recipient_list=[event.hod.email],
        )


def notify_date_suggestion(event):
    """Notify HOD about admin's date/venue suggestion."""
    if event.hod and event.hod.email_notifications:
        _send(
            subject=f"Date Suggestion for: {event.title}",
            template_name='event_suggestion',
            context={'event': event},
            recipient_list=[event.hod.email],
        )


def notify_coordinator_application(coord_request):
    """Notify HOD about a new coordinator application."""
    if coord_request.hod and coord_request.hod.email_notifications:
        _send(
            subject=f"Coordinator Application: {coord_request.student.name}",
            template_name='coordinator_applied',
            context={'req': coord_request},
            recipient_list=[coord_request.hod.email],
        )


def notify_coordinator_status(coord_request):
    """Notify student about coordinator application status."""
    if coord_request.student.email_notifications:
        _send(
            subject=f"Coordinator Application {coord_request.status.title()}: {coord_request.event.title}",
            template_name='coordinator_status',
            context={'req': coord_request},
            recipient_list=[coord_request.student.email],
        )


def notify_user_approved(user_profile):
    """Notify user that their registration was approved."""
    _send(
        subject="Account Approved – Welcome to EduEvent!",
        template_name='user_approved',
        context={'user': user_profile},
        recipient_list=[user_profile.email],
    )


def notify_public_event(event):
    """Notify all students about a new public event."""
    from core.models import UserProfile
    students = UserProfile.objects.filter(
        role__in=['student', 'teacher'],
        is_active=True, is_approved=True, email_notifications=True
    )
    emails = list(students.values_list('email', flat=True))

    _send(
        subject=f"🌐 Open Event: {event.title}",
        template_name='public_event',
        context={
            'event': event,
            'public_url': f"{settings.SITE_URL}/public/event/{event.public_slug}/",
        },
        recipient_list=emails,
    )
