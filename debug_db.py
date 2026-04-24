import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduevent.settings')
django.setup()

from core.models import UserProfile, Event, Venue

print("--- USERS ---")
for u in UserProfile.objects.all():
    print(f"ID: {u.id} | Email: {u.email} | Role: {u.role} | Auth: {u.is_approved}")

print("\n--- EVENTS ---")
for e in Event.objects.all().select_related('hod', 'venue'):
    hod_email = e.hod.email if e.hod else "SYSTEM"
    print(f"ID: {e.id} | Title: {e.title} | Status: {e.status} | HOD: {hod_email} | Venue: {e.venue.name}")
