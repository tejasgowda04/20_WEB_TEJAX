"""
EduEvent – Template Views (Page Rendering)
Serves the existing HTML pages with minimal Django template changes.
"""
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from core.models import Event


# ── Page Views ───────────────────────────────────────────────────

def welcome(request):
    """Welcome / landing page (college intro)."""
    return render(request, 'welcome.html')


def index(request):
    """Role selector entry page."""
    return render(request, 'index.html')


def login_page(request):
    """Login page (role from query param)."""
    role = request.GET.get('role', 'student')
    return render(request, 'pages/login.html', {'role': role})


def register_page(request):
    """Registration page."""
    return render(request, 'pages/register.html')


def admin_dashboard(request):
    """Admin dashboard page."""
    return render(request, 'pages/admin.html')


def hod_dashboard(request):
    """HOD dashboard page."""
    return render(request, 'pages/hod.html')


def student_dashboard(request):
    """Student dashboard page."""
    return render(request, 'pages/student.html')


def teacher_dashboard(request):
    """Teacher dashboard page."""
    return render(request, 'pages/teacher.html')


# ── Public Wall (No Auth Required) ──────────────────────────────

def public_wall(request):
    """Public event wall – no login required."""
    events = Event.objects.filter(
        is_public=True, status='approved'
    ).select_related('venue').order_by('-date')[:50]
    return render(request, 'public/wall.html', {'events': events})


def public_event_detail(request, slug):
    """Individual public event page – shareable link."""
    event = get_object_or_404(Event, public_slug=slug, is_public=True, status='approved')
    share_text = f"🎓 {event.title}\n📅 {event.date.strftime('%d %b %Y')}\n📍 {event.venue_name}\n🔗 "
    share_url = request.build_absolute_uri()
    whatsapp_link = f"https://wa.me/?text={share_text}{share_url}".replace(' ', '%20').replace('\n', '%0A')

    return render(request, 'public/event_detail.html', {
        'event': event,
        'whatsapp_link': whatsapp_link,
        'share_url': share_url,
    })


def college_calendar_page(request):
    """College calendar page."""
    return render(request, 'calendar.html')
