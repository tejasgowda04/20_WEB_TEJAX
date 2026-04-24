"""
EduEvent – Email Trigger API
Lightweight endpoints to trigger email notifications from the frontend.
Works without requiring full Django auth - uses the logged-in user data from localStorage.
"""
import json
import logging
from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from core.models import UserProfile

logger = logging.getLogger(__name__)


def _send_email(subject, html_body, recipient_list):
    """Send an email with error handling."""
    if not recipient_list:
        return False
    try:
        plain = strip_tags(html_body)
        send_mail(
            subject=f"[EduEvent] {subject}",
            message=plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[e for e in recipient_list if e],
            html_message=html_body,
            fail_silently=False,
        )
        logger.info(f"✅ Email sent: '{subject}' to {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"❌ Email error: {e}")
        return False


def _render_email(template_name, context):
    """Render an email template."""
    context.setdefault('college_name', settings.COLLEGE_NAME)
    context.setdefault('site_url', settings.SITE_URL)
    try:
        return render_to_string(f'email/{template_name}.html', context)
    except Exception as e:
        logger.error(f"Template render error: {e}")
        return None


def _get_emails_by_role(role):
    """Get all active emails for a given role from the database."""
    try:
        return list(UserProfile.objects.filter(
            role=role, is_active=True, is_approved=True, email_notifications=True
        ).values_list('email', flat=True))
    except Exception:
        return []


def _get_admin_emails():
    """Get all admin emails."""
    try:
        emails = list(UserProfile.objects.filter(
            role='admin', is_active=True, email_notifications=True
        ).values_list('email', flat=True))
        return emails if emails else [settings.EMAIL_HOST_USER]
    except Exception:
        return [settings.EMAIL_HOST_USER]


def _get_branch_student_emails(branch):
    """Get student emails for a branch."""
    try:
        return list(UserProfile.objects.filter(
            role='student', branch=branch,
            is_active=True, is_approved=True, email_notifications=True
        ).values_list('email', flat=True))
    except Exception:
        return []


def _get_all_student_teacher_emails():
    """Get all student and teacher emails."""
    try:
        return list(UserProfile.objects.filter(
            role__in=['student', 'teacher'],
            is_active=True, is_approved=True, email_notifications=True
        ).values_list('email', flat=True))
    except Exception:
        return []


def _json_body(request):
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return {}


# ═══════════════════════════════════════════════════════════════════
# EMAIL TRIGGER ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@csrf_exempt
@require_POST
def trigger_new_event_email(request):
    """HOD created a new event → email all admins."""
    data = _json_body(request)
    event_title = data.get('title', 'Untitled Event')
    hod_name = data.get('hod_name', 'Unknown')
    branch = data.get('branch', '')
    event_date = data.get('date', '')
    venue_name = data.get('venue_name', '')
    category = data.get('category', '')
    hod_email = data.get('hod_email', '')

    # Build email context (simulating an event object for the template)
    class EventProxy:
        pass
    event = EventProxy()
    event.title = event_title
    event.branch = branch
    event.date = event_date
    event.venue_name = venue_name
    event.category = category

    admin_emails = _get_admin_emails()
    html = _render_email('new_event', {'event': event, 'hod_name': hod_name})
    if html:
        sent = _send_email(f"New Event Request: {event_title}", html, admin_emails)
        return JsonResponse({'success': sent, 'sent_to': len(admin_emails)})
    return JsonResponse({'success': False, 'error': 'Template render failed.'})


@csrf_exempt
@require_POST
def trigger_event_approved_email(request):
    """Admin approved event → email HOD + branch students."""
    data = _json_body(request)
    event_title = data.get('title', '')
    branch = data.get('branch', '')
    hod_email = data.get('hod_email', '')
    venue_name = data.get('venue_name', '')
    event_date = data.get('date', '')
    admin_note = data.get('admin_note', '')

    class EventProxy:
        pass
    event = EventProxy()
    event.title = event_title
    event.branch = branch
    event.date = event_date
    event.venue_name = venue_name
    event.admin_note = admin_note
    event.status = 'approved'

    recipients = []
    if hod_email:
        recipients.append(hod_email)
    recipients.extend(_get_branch_student_emails(branch))
    recipients = list(set(recipients))

    html = _render_email('event_approved', {'event': event})
    if html and recipients:
        sent = _send_email(f"Event Approved: {event_title}", html, recipients)
        return JsonResponse({'success': sent, 'sent_to': len(recipients)})
    return JsonResponse({'success': False, 'error': 'No recipients or template error.'})


@csrf_exempt
@require_POST
def trigger_event_rejected_email(request):
    """Admin rejected event → email HOD."""
    data = _json_body(request)
    event_title = data.get('title', '')
    hod_email = data.get('hod_email', '')
    admin_note = data.get('admin_note', '')
    event_date = data.get('date', '')
    branch = data.get('branch', '')

    class EventProxy:
        pass
    event = EventProxy()
    event.title = event_title
    event.branch = branch
    event.date = event_date
    event.admin_note = admin_note
    event.status = 'rejected'

    if not hod_email:
        return JsonResponse({'success': False, 'error': 'No HOD email.'})

    html = _render_email('event_rejected', {'event': event})
    if html:
        sent = _send_email(f"Event Rejected: {event_title}", html, [hod_email])
        return JsonResponse({'success': sent})
    return JsonResponse({'success': False, 'error': 'Template error.'})


@csrf_exempt
@require_POST
def trigger_date_suggestion_email(request):
    """Admin suggested new date → email HOD."""
    data = _json_body(request)
    event_title = data.get('title', '')
    hod_email = data.get('hod_email', '')
    suggested_date = data.get('suggested_date', '')
    suggested_venue = data.get('suggested_venue', '')
    admin_note = data.get('admin_note', '')
    original_date = data.get('date', '')

    class EventProxy:
        pass
    event = EventProxy()
    event.title = event_title
    event.date = original_date
    event.suggested_date = suggested_date
    event.suggested_venue_name = suggested_venue
    event.admin_note = admin_note

    if not hod_email:
        return JsonResponse({'success': False, 'error': 'No HOD email.'})

    html = _render_email('event_suggestion', {'event': event})
    if html:
        sent = _send_email(f"Date Suggestion for: {event_title}", html, [hod_email])
        return JsonResponse({'success': sent})
    return JsonResponse({'success': False, 'error': 'Template error.'})


@csrf_exempt
@require_POST
def trigger_coordinator_email(request):
    """Student applied as coordinator → email HOD.
       OR HOD approved/rejected → email student."""
    data = _json_body(request)
    action = data.get('action', 'applied')  # 'applied', 'approved', 'rejected'

    if action == 'applied':
        # Notify HOD
        student_name = data.get('student_name', '')
        student_branch = data.get('student_branch', '')
        event_title = data.get('event_title', '')
        hod_email = data.get('hod_email', '')
        message = data.get('message', '')

        class ReqProxy:
            pass
        req = ReqProxy()

        class StudentProxy:
            pass
        req.student = StudentProxy()
        req.student.name = student_name
        req.student.branch = student_branch
        req.student.email = data.get('student_email', '')

        class EvProxy:
            pass
        req.event = EvProxy()
        req.event.title = event_title
        req.message = message

        if hod_email:
            html = _render_email('coordinator_applied', {'req': req})
            if html:
                sent = _send_email(f"Coordinator Application: {student_name}", html, [hod_email])
                return JsonResponse({'success': sent})

    else:
        # Notify student (approved/rejected)
        student_email = data.get('student_email', '')
        event_title = data.get('event_title', '')

        class ReqProxy:
            pass
        req = ReqProxy()
        req.status = action

        class EvProxy:
            pass
        req.event = EvProxy()
        req.event.title = event_title

        class StudentProxy:
            pass
        req.student = StudentProxy()
        req.student.name = data.get('student_name', '')

        if student_email:
            html = _render_email('coordinator_status', {'req': req})
            if html:
                sent = _send_email(
                    f"Coordinator Application {action.title()}: {event_title}",
                    html, [student_email]
                )
                return JsonResponse({'success': sent})

    return JsonResponse({'success': False, 'error': 'Missing data.'})


@csrf_exempt
@require_POST
def trigger_user_approved_email(request):
    """Admin approved a user → email the user."""
    data = _json_body(request)
    user_email = data.get('email', '')
    user_name = data.get('name', '')
    user_role = data.get('role', '')

    if not user_email:
        return JsonResponse({'success': False, 'error': 'No email.'})

    class UserProxy:
        pass
    user = UserProxy()
    user.name = user_name
    user.role = user_role
    user.email = user_email

    html = _render_email('user_approved', {'user': user})
    if html:
        sent = _send_email("Account Approved – Welcome to EduEvent!", html, [user_email])
        return JsonResponse({'success': sent})
    return JsonResponse({'success': False, 'error': 'Template error.'})
