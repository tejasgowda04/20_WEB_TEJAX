"""
EduEvent – REST API Views
Handles all CRUD operations, conflict detection, auth, notifications.
All endpoints return JSON. Frontend JS calls these via fetch().
"""
import json
from datetime import date, timedelta
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.db.models import Q, Count
from django.utils import timezone
from django.conf import settings
from core.models import (
    UserProfile, Event, Venue, EventTemplate,
    CoordinatorRequest, Notification, CollegeCalendarEntry
)
from core import email_service


# ── Helper: Get current user from session or Firebase token ──────

def get_current_user(request):
    """Extract the authenticated user profile from the session."""
    uid = request.session.get('user_id')
    if not uid:
        return None
    try:
        return UserProfile.objects.get(id=uid, is_active=True)
    except UserProfile.DoesNotExist:
        return None


def require_user(request, allowed_roles=None):
    """Returns user or error response."""
    user = get_current_user(request)
    if not user:
        return None, JsonResponse({'error': 'Not authenticated'}, status=401)
    if allowed_roles and user.role not in allowed_roles:
        return None, JsonResponse({'error': 'Forbidden'}, status=403)
    return user, None


def json_body(request):
    """Parse JSON body from request."""
    try:
        return json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return {}


# ═══════════════════════════════════════════════════════════════════
# AUTH ENDPOINTS
# ═══════════════════════════════════════════════════════════════════

@csrf_exempt
@require_POST
def api_register(request):
    """Register a new user. Links to Firebase UID."""
    data = json_body(request)
    role = data.get('role', '').lower()
    email = data.get('email', '').strip().lower()
    name = data.get('name', '').strip()
    phone = data.get('phone', '').strip()
    branch = data.get('branch', '').strip()
    firebase_uid = data.get('firebase_uid', '').strip()

    if not all([role, email, name, branch, firebase_uid]):
        return JsonResponse({'error': 'All fields are required.'}, status=400)

    if role not in ['hod', 'student', 'teacher']:
        return JsonResponse({'error': 'Invalid role.'}, status=400)

    if UserProfile.objects.filter(email=email).exists():
        return JsonResponse({'error': 'Email already registered.'}, status=400)

    extra = {}
    if role == 'student':
        extra = {'roll_no': data.get('roll_no', ''), 'year': data.get('year', '')}
    elif role == 'hod':
        extra = {'department': data.get('department', branch), 'designation': data.get('designation', '')}
    elif role == 'teacher':
        extra = {'subject': data.get('subject', ''), 'emp_id': data.get('emp_id', '')}

    profile = UserProfile.objects.create(
        firebase_uid=firebase_uid,
        email=email,
        name=name,
        phone=phone,
        role=role,
        branch=branch,
        extra_data=extra,
        is_approved=False,
    )

    # Notify admin via push notification
    Notification.objects.create(
        target_role='admin',
        message=f"New {role} registration: {name} ({email}) awaiting approval.",
        link='/dashboard/admin/#users',
    )
    
    # Notify admin via SMTP email
    email_service.notify_new_user_registration(profile)

    return JsonResponse({'success': True, 'message': 'Registration successful. Pending admin approval.'})


@csrf_exempt
@require_POST
def api_login(request):
    """Login: verify Firebase UID and create session."""
    data = json_body(request)
    firebase_uid = data.get('firebase_uid', '').strip()
    email = data.get('email', '').strip().lower()
    role = data.get('role', '').strip().lower()

    if not firebase_uid or not email:
        return JsonResponse({'error': 'Invalid credentials.'}, status=400)

    try:
        # First check if the user exists at all
        user = UserProfile.objects.get(Q(firebase_uid=firebase_uid) | Q(email=email))
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': f'No account found with email {email}. Please register first.'}, status=404)
    except UserProfile.MultipleObjectsReturned:
        # Fallback to specific role if multiple found (unlikely due to unique email)
        user = UserProfile.objects.filter(Q(firebase_uid=firebase_uid) | Q(email=email), role=role).first()
        if not user:
             return JsonResponse({'error': 'Conflicting account roles. Contact admin.'}, status=400)

    # Now verify if the role matches the portal they are trying to access
    if user.role != role:
        return JsonResponse({
            'error': f'Access Denied: Your account is registered as a {user.role.upper()}, but you are trying to login to the {role.upper()} portal. Please use the correct role selection.',
            'correct_role': user.role
        }, status=403)

    if not user.is_active:
        return JsonResponse({'error': 'Account deactivated. Contact admin.'}, status=403)
    if not user.is_approved and user.role != 'admin':
        return JsonResponse({'error': 'Account pending admin approval.'}, status=403)

    # Update Firebase UID if needed
    if user.firebase_uid != firebase_uid:
        user.firebase_uid = firebase_uid
        user.save(update_fields=['firebase_uid'])

    # Create Django session
    request.session['user_id'] = str(user.id)
    request.session['user_role'] = user.role
    request.session['user_name'] = user.name
    request.session['user_email'] = user.email
    request.session['user_branch'] = user.branch

    return JsonResponse({
        'success': True,
        'user': _user_json(user),
    })


def api_firebase_config(request):
    """Return Firebase public configs for JS SDK."""
    return JsonResponse({
        'apiKey': settings.FIREBASE_API_KEY,
        'authDomain': settings.FIREBASE_AUTH_DOMAIN,
        'projectId': settings.FIREBASE_PROJECT_ID,
        'storageBucket': settings.FIREBASE_STORAGE_BUCKET,
        'messagingSenderId': settings.FIREBASE_MESSAGING_SENDER_ID,
        'appId': settings.FIREBASE_APP_ID,
    })


@csrf_exempt
@require_POST
def api_logout(request):
    """Logout: clear session."""
    request.session.flush()
    return JsonResponse({'success': True})


@csrf_exempt
def api_me(request):
    """Get current logged-in user profile."""
    user = get_current_user(request)
    if not user:
        return JsonResponse({'error': 'Not authenticated'}, status=401)
    return JsonResponse({'user': _user_json(user)})


def _user_json(u):
    return {
        'id': str(u.id),
        'firebase_uid': u.firebase_uid,
        'email': u.email,
        'name': u.name,
        'phone': u.phone,
        'role': u.role,
        'branch': u.branch,
        'is_approved': u.is_approved,
        'is_active': u.is_active,
        'extra_data': u.extra_data,
        'initials': u.initials,
        'created_at': u.created_at.isoformat(),
    }


# ═══════════════════════════════════════════════════════════════════
# EVENTS API
# ═══════════════════════════════════════════════════════════════════

def api_events(request):
    """GET: List events with optional filters."""
    user, err = require_user(request)
    if err:
        return err

    events = Event.objects.select_related('venue', 'hod').all()

    # Filters
    status = request.GET.get('status')
    branch = request.GET.get('branch')
    hod_id = request.GET.get('hod_id')
    venue_id = request.GET.get('venue_id')
    category = request.GET.get('category')
    time_filter = request.GET.get('time')
    search = request.GET.get('search', '').strip()

    if status:
        events = events.filter(status=status)
    if branch:
        events = events.filter(branch=branch)
    if hod_id:
        events = events.filter(hod_id=hod_id)
    if venue_id:
        events = events.filter(venue_id=venue_id)
    if category:
        events = events.filter(category=category)
    if time_filter == 'upcoming':
        events = events.filter(date__gte=date.today())
    elif time_filter == 'past':
        events = events.filter(date__lt=date.today())
    if search:
        events = events.filter(
            Q(title__icontains=search) | Q(branch__icontains=search) | Q(organizer__icontains=search)
        )

    # Role-based filtering
    if user.role == 'student' or user.role == 'teacher':
        events = events.filter(status='approved')
    elif user.role == 'hod':
        events = events.filter(Q(status='approved') | Q(hod_id=str(user.id)))

    data = [_event_json(e) for e in events[:200]]
    return JsonResponse({'events': data})


@csrf_exempt
@require_POST
def api_create_event(request):
    """HOD creates a new event request."""
    user, err = require_user(request, ['hod', 'admin'])
    if err:
        return err

    data = json_body(request)
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    event_date = data.get('date', '')
    end_date = data.get('end_date', '') or event_date
    venue_id = data.get('venue_id', '')
    category = data.get('category', 'Other')
    attendees = int(data.get('expected_attendees', 100))
    organizer = data.get('organizer', user.name)
    template_id = data.get('template_id')
    is_public = data.get('is_public', False)
    public_description = data.get('public_description', '')

    if not all([title, description, event_date, venue_id]):
        return JsonResponse({'error': 'Required fields missing.'}, status=400)

    try:
        venue = Venue.objects.get(id=venue_id, is_active=True)
    except Venue.DoesNotExist:
        return JsonResponse({'error': 'Invalid venue.'}, status=400)

    event = Event.objects.create(
        title=title,
        description=description,
        date=event_date,
        end_date=end_date,
        venue=venue,
        branch=user.branch or data.get('branch', ''),
        organizer=organizer,
        hod=user if user.role == 'hod' else None,
        category=category,
        expected_attendees=attendees,
        status='pending',
        template_id=template_id,
        is_public=is_public,
        public_description=public_description,
    )

    # Notification
    Notification.objects.create(
        target_role='admin',
        message=f'New event request: "{event.title}" from {event.branch} on {event.date} at {venue.name}.',
        link='/dashboard/admin/#pendingEvents',
    )

    # Email notification
    email_service.notify_new_event_request(event)

    event.refresh_from_db()
    return JsonResponse({'success': True, 'event': _event_json(event)})


@csrf_exempt
@require_POST
def api_update_event(request, event_id):
    """Admin updates event (approve/reject/suggest)."""
    user, err = require_user(request, ['admin'])
    if err:
        return err

    try:
        event = Event.objects.select_related('venue', 'hod').get(id=event_id)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found.'}, status=404)

    data = json_body(request)
    action = data.get('action', '')

    if action == 'approve':
        event.status = 'approved'
        event.admin_note = data.get('note', '')
        event.save()
        Notification.objects.create(
            user=event.hod,
            message=f'Your event "{event.title}" has been APPROVED! 🎉',
        )
        email_service.notify_event_approved(event)
        if event.is_public:
            email_service.notify_public_event(event)

    elif action == 'reject':
        event.status = 'rejected'
        event.admin_note = data.get('note', '')
        event.save()
        Notification.objects.create(
            user=event.hod,
            message=f'Your event "{event.title}" has been REJECTED. Reason: {event.admin_note}',
        )
        email_service.notify_event_rejected(event)

    elif action == 'suggest':
        new_date = data.get('suggested_date')
        new_venue_id = data.get('suggested_venue_id')
        if new_date:
            event.suggested_date = new_date
        if new_venue_id:
            try:
                event.suggested_venue = Venue.objects.get(id=new_venue_id)
            except Venue.DoesNotExist:
                pass
        event.admin_note = data.get('note', '')
        event.save()
        Notification.objects.create(
            user=event.hod,
            message=f'Admin suggested a new date for "{event.title}". Please review.',
        )
        email_service.notify_date_suggestion(event)

    elif action == 'make_public':
        event.is_public = True
        event.public_description = data.get('public_description', event.description)
        event.save()
        if event.status == 'approved':
            email_service.notify_public_event(event)

    elif action == 'delete':
        event.delete()
        return JsonResponse({'success': True, 'deleted': True})

    # General field updates
    for field in ['title', 'description', 'category', 'expected_attendees']:
        if field in data:
            setattr(event, field, data[field])
    event.save()

    event.refresh_from_db()
    return JsonResponse({'success': True, 'event': _event_json(event)})


@csrf_exempt
@require_POST
def api_hod_respond_suggestion(request, event_id):
    """HOD accepts or declines admin's date suggestion."""
    user, err = require_user(request, ['hod'])
    if err:
        return err

    try:
        event = Event.objects.get(id=event_id, hod=user)
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found.'}, status=404)

    data = json_body(request)
    accept = data.get('accept', False)

    if accept and event.suggested_date:
        event.date = event.suggested_date
        if event.suggested_venue:
            event.venue = event.suggested_venue
        event.status = 'approved'
    event.suggested_date = None
    event.suggested_venue = None
    event.save()

    Notification.objects.create(
        target_role='admin',
        message=f'HOD {"accepted" if accept else "declined"} the suggested date for "{event.title}".',
    )

    return JsonResponse({'success': True, 'event': _event_json(event)})


# ═══════════════════════════════════════════════════════════════════
# CONFLICT DETECTION API
# ═══════════════════════════════════════════════════════════════════

def api_check_conflicts(request):
    """Check for venue/date conflicts. Used by HOD form in real-time."""
    venue_id = request.GET.get('venue_id', '')
    event_date = request.GET.get('date', '')
    end_date = request.GET.get('end_date', '') or event_date
    exclude_id = request.GET.get('exclude_id', '')

    if not venue_id or not event_date:
        return JsonResponse({'conflicts': []})

    conflicts = Event.objects.filter(
        venue_id=venue_id,
        status__in=['pending', 'approved'],
    ).exclude(id=exclude_id if exclude_id else None)

    # Check date overlap
    result = []
    for ev in conflicts:
        ev_start = ev.date
        ev_end = ev.end_date or ev.date
        q_start = date.fromisoformat(event_date)
        q_end = date.fromisoformat(end_date)

        if not (q_end < ev_start or q_start > ev_end):
            result.append(_event_json(ev))

    return JsonResponse({'conflicts': result, 'has_conflicts': len(result) > 0})


def api_detect_all_conflicts(request):
    """Admin: detect all scheduling conflicts system-wide."""
    user, err = require_user(request, ['admin'])
    if err:
        return err

    events = list(Event.objects.filter(status__in=['pending', 'approved']).select_related('venue'))
    conflicts = []

    for i, a in enumerate(events):
        for b in events[i+1:]:
            if a.venue_id != b.venue_id:
                continue
            a_end = a.end_date or a.date
            b_end = b.end_date or b.date
            if not (a_end < b.date or a.date > b_end):
                conflicts.append({
                    'event_a': _event_json(a),
                    'event_b': _event_json(b),
                    'venue': a.venue_name,
                })

    return JsonResponse({'conflicts': conflicts, 'count': len(conflicts)})


# ═══════════════════════════════════════════════════════════════════
# VENUES API
# ═══════════════════════════════════════════════════════════════════

def api_venues(request):
    """List all active venues with booking info."""
    venues = Venue.objects.filter(is_active=True)
    data = []
    today = date.today()

    for v in venues:
        booked_today = Event.objects.filter(
            venue=v, status='approved',
            date__lte=today, end_date__gte=today
        ).count()
        upcoming = Event.objects.filter(
            venue=v, status='approved', date__gt=today
        ).count()
        total = Event.objects.filter(venue=v, status='approved').count()

        data.append({
            'id': v.id,
            'name': v.name,
            'capacity': v.capacity,
            'description': v.description,
            'is_available': booked_today == 0,
            'booked_today': booked_today,
            'upcoming_count': upcoming,
            'total_booked': total,
        })

    return JsonResponse({'venues': data})


# ═══════════════════════════════════════════════════════════════════
# EVENT TEMPLATES API
# ═══════════════════════════════════════════════════════════════════

def api_templates(request):
    """List event templates."""
    user, err = require_user(request, ['admin', 'hod'])
    if err:
        return err

    templates = EventTemplate.objects.filter(is_active=True).select_related('default_venue')
    data = [{
        'id': str(t.id),
        'title': t.title,
        'description': t.description,
        'category': t.category,
        'default_venue_id': t.default_venue_id,
        'default_venue_name': t.default_venue.name if t.default_venue else '',
        'default_branch': t.default_branch,
        'expected_attendees': t.expected_attendees,
        'frequency': t.frequency,
        'frequency_display': t.get_frequency_display(),
        'typical_month': t.typical_month,
        'typical_duration_days': t.typical_duration_days,
    } for t in templates]

    return JsonResponse({'templates': data})


@csrf_exempt
@require_POST
def api_create_template(request):
    """Admin creates a new event template."""
    user, err = require_user(request, ['admin'])
    if err:
        return err

    data = json_body(request)
    template = EventTemplate.objects.create(
        title=data.get('title', ''),
        description=data.get('description', ''),
        category=data.get('category', 'Other'),
        default_venue_id=data.get('default_venue_id') or None,
        default_branch=data.get('default_branch', ''),
        expected_attendees=int(data.get('expected_attendees', 100)),
        frequency=data.get('frequency', 'yearly'),
        typical_month=data.get('typical_month') or None,
        typical_duration_days=int(data.get('typical_duration_days', 1)),
        created_by=user,
    )

    return JsonResponse({'success': True, 'id': str(template.id)})


# ═══════════════════════════════════════════════════════════════════
# COORDINATOR REQUESTS API
# ═══════════════════════════════════════════════════════════════════

def api_coordinator_requests(request):
    """List coordinator requests."""
    user, err = require_user(request)
    if err:
        return err

    reqs = CoordinatorRequest.objects.select_related('student', 'event', 'hod').all()

    if user.role == 'student':
        reqs = reqs.filter(student=user)
    elif user.role == 'hod':
        reqs = reqs.filter(hod=user)

    data = [{
        'id': str(r.id),
        'student_id': str(r.student_id),
        'student_name': r.student.name,
        'student_branch': r.student.branch,
        'student_year': r.student.extra_data.get('year', ''),
        'student_email': r.student.email,
        'event_id': str(r.event_id),
        'event_title': r.event.title,
        'hod_id': str(r.hod_id) if r.hod_id else '',
        'message': r.message,
        'status': r.status,
        'created_at': r.created_at.isoformat(),
    } for r in reqs]

    return JsonResponse({'requests': data})


@csrf_exempt
@require_POST
def api_apply_coordinator(request):
    """Student applies as coordinator."""
    user, err = require_user(request, ['student'])
    if err:
        return err

    data = json_body(request)
    event_id = data.get('event_id')
    message = data.get('message', '')

    try:
        event = Event.objects.get(id=event_id, status='approved')
    except Event.DoesNotExist:
        return JsonResponse({'error': 'Event not found.'}, status=404)

    if CoordinatorRequest.objects.filter(student=user, event=event).exists():
        return JsonResponse({'error': 'Already applied.'}, status=400)

    req = CoordinatorRequest.objects.create(
        student=user,
        event=event,
        hod=event.hod,
        message=message,
    )

    if event.hod:
        Notification.objects.create(
            user=event.hod,
            message=f'Student {user.name} applied as coordinator for "{event.title}".',
        )
    email_service.notify_coordinator_application(req)

    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def api_update_coordinator(request, req_id):
    """HOD approves/rejects coordinator request."""
    user, err = require_user(request, ['hod', 'admin'])
    if err:
        return err

    try:
        req = CoordinatorRequest.objects.select_related('student', 'event').get(id=req_id)
    except CoordinatorRequest.DoesNotExist:
        return JsonResponse({'error': 'Request not found.'}, status=404)

    data = json_body(request)
    new_status = data.get('status', '')
    if new_status in ['approved', 'rejected']:
        req.status = new_status
        req.save()
        Notification.objects.create(
            user=req.student,
            message=f'Your coordinator application for "{req.event.title}" has been {new_status.upper()}.',
        )
        email_service.notify_coordinator_status(req)

    return JsonResponse({'success': True})


# ═══════════════════════════════════════════════════════════════════
# USERS API (Admin only)
# ═══════════════════════════════════════════════════════════════════

def api_users(request):
    """Admin: list all users."""
    user, err = require_user(request, ['admin'])
    if err:
        return err

    role_filter = request.GET.get('role', '')
    pending_only = request.GET.get('pending', '') == 'true'

    users = UserProfile.objects.all()
    if role_filter:
        users = users.filter(role=role_filter)
    if pending_only:
        users = users.filter(is_approved=False)

    data = [_user_json(u) for u in users]
    return JsonResponse({'users': data})


@csrf_exempt
@require_POST
def api_approve_user(request, user_id):
    """Admin approves a user."""
    admin, err = require_user(request, ['admin'])
    if err:
        return err

    try:
        target = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found.'}, status=404)

    target.is_approved = True
    target.save(update_fields=['is_approved'])

    email_service.notify_user_approved(target)
    Notification.objects.create(
        user=target,
        message='Your EduEvent account has been approved! You can now log in. 🎉',
    )

    return JsonResponse({'success': True})


@csrf_exempt
@require_POST
def api_deactivate_user(request, user_id):
    """Admin deactivates a user."""
    admin, err = require_user(request, ['admin'])
    if err:
        return err

    try:
        target = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist:
        return JsonResponse({'error': 'User not found.'}, status=404)

    target.is_active = False
    target.save(update_fields=['is_active'])

    return JsonResponse({'success': True})


# ═══════════════════════════════════════════════════════════════════
# NOTIFICATIONS API
# ═══════════════════════════════════════════════════════════════════

def api_notifications(request):
    """Get notifications for current user."""
    user, err = require_user(request)
    if err:
        return err

    notifs = Notification.objects.filter(
        Q(user=user) | Q(target_role=user.role) | Q(target_role='all')
    ).order_by('-created_at')[:100]

    data = [{
        'id': str(n.id),
        'message': n.message,
        'is_read': n.is_read,
        'link': n.link,
        'created_at': n.created_at.isoformat(),
    } for n in notifs]

    unread = notifs.filter(is_read=False).count()
    return JsonResponse({'notifications': data, 'unread_count': unread})


@csrf_exempt
@require_POST
def api_mark_read(request, notif_id):
    """Mark notification as read."""
    user, err = require_user(request)
    if err:
        return err

    try:
        notif = Notification.objects.get(id=notif_id)
        notif.is_read = True
        notif.save(update_fields=['is_read'])
    except Notification.DoesNotExist:
        pass

    return JsonResponse({'success': True})


# ═══════════════════════════════════════════════════════════════════
# COLLEGE CALENDAR API
# ═══════════════════════════════════════════════════════════════════

def api_calendar(request):
    """Get calendar entries (holidays, exams, events)."""
    user, err = require_user(request)
    if err:
        return err

    year = int(request.GET.get('year', date.today().year))
    entries = CollegeCalendarEntry.objects.filter(
        Q(date__year=year) | Q(is_recurring_yearly=True)
    )

    data = [{
        'id': str(e.id),
        'title': e.title,
        'date': e.date.isoformat(),
        'end_date': e.end_date.isoformat() if e.end_date else None,
        'type': e.entry_type,
        'type_display': e.get_entry_type_display(),
        'description': e.description,
        'is_recurring': e.is_recurring_yearly,
    } for e in entries]

    # Also include approved events
    events = Event.objects.filter(
        status='approved', date__year=year
    ).select_related('venue')

    event_data = [{
        'id': str(ev.id),
        'title': ev.title,
        'date': ev.date.isoformat(),
        'end_date': ev.end_date.isoformat() if ev.end_date else None,
        'type': 'event',
        'type_display': 'Approved Event',
        'description': f"{ev.branch} | {ev.venue_name}",
        'is_recurring': False,
    } for ev in events]

    return JsonResponse({'entries': data + event_data})


@csrf_exempt
@require_POST
def api_create_calendar_entry(request):
    """Admin creates a calendar entry."""
    user, err = require_user(request, ['admin'])
    if err:
        return err

    data = json_body(request)
    entry = CollegeCalendarEntry.objects.create(
        title=data.get('title', ''),
        date=data.get('date'),
        end_date=data.get('end_date') or None,
        entry_type=data.get('type', 'other'),
        description=data.get('description', ''),
        is_recurring_yearly=data.get('is_recurring', False),
        created_by=user,
    )

    return JsonResponse({'success': True, 'id': str(entry.id)})


@csrf_exempt
@require_POST
def api_delete_calendar_entry(request, entry_id):
    """Admin deletes a calendar entry."""
    user, err = require_user(request, ['admin'])
    if err:
        return err

    CollegeCalendarEntry.objects.filter(id=entry_id).delete()
    return JsonResponse({'success': True})


# ═══════════════════════════════════════════════════════════════════
# ANALYTICS API
# ═══════════════════════════════════════════════════════════════════

def api_analytics(request):
    """Admin: dashboard analytics."""
    user, err = require_user(request, ['admin'])
    if err:
        return err

    events = Event.objects.all()
    users = UserProfile.objects.all()

    BRANCHES = [
        'Computer Science', 'Information Technology', 'Electronics',
        'Mechanical', 'Civil', 'Electrical', 'MBA', 'MCA'
    ]

    by_branch = {b: events.filter(branch=b).count() for b in BRANCHES}
    by_category = {c: events.filter(category=c).count() for c in ['Technical','Cultural','Sports','Seminar','Workshop','Other']}
    by_venue = {v.name: events.filter(venue=v).count() for v in Venue.objects.all()}

    total = events.count() or 1
    approved = events.filter(status='approved').count()
    pending = events.filter(status='pending').count()
    rejected = events.filter(status='rejected').count()

    return JsonResponse({
        'total_events': events.count(),
        'total_users': users.count(),
        'approved': approved,
        'pending': pending,
        'rejected': rejected,
        'approval_rate': round(approved / total * 100),
        'by_branch': by_branch,
        'by_category': by_category,
        'by_venue': by_venue,
        'pending_users': users.filter(is_approved=False).count(),
    })


# ═══════════════════════════════════════════════════════════════════
# BRANCHES LIST
# ═══════════════════════════════════════════════════════════════════

def api_branches(request):
    """List available branches/departments."""
    branches = [
        'Computer Science', 'Information Technology', 'Electronics',
        'Mechanical', 'Civil', 'Electrical', 'MBA', 'MCA'
    ]
    return JsonResponse({'branches': branches})


# ── Private Helpers ──────────────────────────────────────────────

def _event_json(e):
    return {
        'id': str(e.id),
        'title': e.title,
        'description': e.description,
        'date': e.date.isoformat(),
        'end_date': e.end_date.isoformat() if e.end_date else None,
        'venue_id': e.venue_id,
        'venue_name': e.venue_name,
        'branch': e.branch,
        'organizer': e.organizer,
        'hod_id': str(e.hod_id) if e.hod_id else '',
        'status': e.status,
        'category': e.category,
        'expected_attendees': e.expected_attendees,
        'admin_note': e.admin_note,
        'suggested_date': e.suggested_date.isoformat() if e.suggested_date else None,
        'suggested_venue_id': e.suggested_venue_id,
        'suggested_venue_name': e.suggested_venue.name if e.suggested_venue else '',
        'is_public': e.is_public,
        'public_slug': e.public_slug or '',
        'is_past': e.is_past,
        'is_upcoming': e.is_upcoming,
        'created_at': e.created_at.isoformat(),
    }
