"""EduEvent – All URL patterns."""
from django.urls import path
from core import views, api_views, email_triggers

urlpatterns = [
    # ── Page Routes (preserving existing structure) ──────────────
    path('', views.welcome, name='welcome'),
    path('index.html', views.index, name='index'),
    path('welcome.html', views.welcome, name='welcome_html'),
    path('pages/login.html', views.login_page, name='login'),
    path('pages/register.html', views.register_page, name='register'),
    path('pages/admin.html', views.admin_dashboard, name='admin_dashboard'),
    path('pages/hod.html', views.hod_dashboard, name='hod_dashboard'),
    path('pages/student.html', views.student_dashboard, name='student_dashboard'),
    path('pages/teacher.html', views.teacher_dashboard, name='teacher_dashboard'),
    path('calendar/', views.college_calendar_page, name='calendar'),

    # ── Public Wall (No Auth) ────────────────────────────────────
    path('public/', views.public_wall, name='public_wall'),
    path('public/event/<slug:slug>/', views.public_event_detail, name='public_event_detail'),

    # ── Auth API ─────────────────────────────────────────────────
    path('api/auth/register/', api_views.api_register, name='api_register'),
    path('api/auth/login/', api_views.api_login, name='api_login'),
    path('api/auth/logout/', api_views.api_logout, name='api_logout'),
    path('api/auth/me/', api_views.api_me, name='api_me'),
    path('api/auth/firebase-config/', api_views.api_firebase_config, name='api_firebase_config'),

    # ── Events API ───────────────────────────────────────────────
    path('api/events/', api_views.api_events, name='api_events'),
    path('api/events/create/', api_views.api_create_event, name='api_create_event'),
    path('api/events/<uuid:event_id>/update/', api_views.api_update_event, name='api_update_event'),
    path('api/events/<uuid:event_id>/hod-respond/', api_views.api_hod_respond_suggestion, name='api_hod_respond'),

    # ── Conflict Detection API ───────────────────────────────────
    path('api/conflicts/check/', api_views.api_check_conflicts, name='api_check_conflicts'),
    path('api/conflicts/all/', api_views.api_detect_all_conflicts, name='api_all_conflicts'),

    # ── Venues API ───────────────────────────────────────────────
    path('api/venues/', api_views.api_venues, name='api_venues'),

    # ── Templates API ────────────────────────────────────────────
    path('api/templates/', api_views.api_templates, name='api_templates'),
    path('api/templates/create/', api_views.api_create_template, name='api_create_template'),

    # ── Coordinator Requests API ─────────────────────────────────
    path('api/coordinators/', api_views.api_coordinator_requests, name='api_coord_requests'),
    path('api/coordinators/apply/', api_views.api_apply_coordinator, name='api_apply_coord'),
    path('api/coordinators/<uuid:req_id>/update/', api_views.api_update_coordinator, name='api_update_coord'),

    # ── Users API (Admin) ────────────────────────────────────────
    path('api/users/', api_views.api_users, name='api_users'),
    path('api/users/<uuid:user_id>/approve/', api_views.api_approve_user, name='api_approve_user'),
    path('api/users/<uuid:user_id>/deactivate/', api_views.api_deactivate_user, name='api_deactivate_user'),

    # ── Notifications API ────────────────────────────────────────
    path('api/notifications/', api_views.api_notifications, name='api_notifications'),
    path('api/notifications/<uuid:notif_id>/read/', api_views.api_mark_read, name='api_mark_read'),

    # ── Calendar API ─────────────────────────────────────────────
    path('api/calendar/', api_views.api_calendar, name='api_calendar'),
    path('api/calendar/create/', api_views.api_create_calendar_entry, name='api_create_calendar'),
    path('api/calendar/<uuid:entry_id>/delete/', api_views.api_delete_calendar_entry, name='api_delete_calendar'),

    # ── Analytics API ────────────────────────────────────────────
    path('api/analytics/', api_views.api_analytics, name='api_analytics'),

    # ── Utils API ────────────────────────────────────────────────
    path('api/branches/', api_views.api_branches, name='api_branches'),

    # ── Email Trigger Endpoints (called by frontend for notifications) ──
    path('api/email/new-event/', email_triggers.trigger_new_event_email, name='email_new_event'),
    path('api/email/event-approved/', email_triggers.trigger_event_approved_email, name='email_event_approved'),
    path('api/email/event-rejected/', email_triggers.trigger_event_rejected_email, name='email_event_rejected'),
    path('api/email/date-suggestion/', email_triggers.trigger_date_suggestion_email, name='email_date_suggestion'),
    path('api/email/coordinator/', email_triggers.trigger_coordinator_email, name='email_coordinator'),
    path('api/email/user-approved/', email_triggers.trigger_user_approved_email, name='email_user_approved'),
]

