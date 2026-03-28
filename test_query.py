import os
import django
from django.db.models import Q

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduevent.settings')
django.setup()

from core.models import UserProfile, Event

def test_hod_query(hod_email):
    hod = UserProfile.objects.get(email=hod_email)
    print(f"DEBUG: HOD Name: {hod.name}, ID: {hod.id}")
    
    # Simulate api_events query for HOD
    events = Event.objects.filter(Q(status='approved') | Q(hod_id=str(hod.id)))
    print(f"QUERY: Event.objects.filter(Q(status='approved') | Q(hod_id='{str(hod.id)}'))")
    print(f"FOUND EVENTS COUNT: {events.count()}")
    for e in events:
        print(f"  - {e.title} (Status: {e.status}, HOD_ID: {e.hod_id})")

if __name__ == "__main__":
    # Test with hod.cs@college.edu
    try:
        test_hod_query("hod.cs@college.edu")
    except Exception as e:
        print(f"Error: {e}")
