import os
import django
import json
from django.test import RequestFactory
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eduevent.settings')
django.setup()

from core import api_views
from core.models import UserProfile, Venue, Event

def test_event_submission():
    # Get an HOD
    hod = UserProfile.objects.filter(role='hod', is_approved=True).first()
    if not hod:
        print("Error: No HOD found in DB")
        return
    print(f"DEBUG: Using HOD {hod.email}")
    
    venue = Venue.objects.first()
    
    # Create request object
    rf = RequestFactory()
    data = {
        'title': 'Test Script Event',
        'description': 'This event was created by a python debug script.',
        'date': '2026-05-10',
        'venue_id': venue.id,
        'category': 'Technical',
        'expected_attendees': 200,
        'organizer': hod.name,
    }
    
    req = rf.post('/api/events/create/', data=json.dumps(data), content_type='application/json')
    req.session = {'user_id': str(hod.id)}
    
    # call view directly
    resp = api_views.api_create_event(req)
    print("STATUS:", resp.status_code)
    print("RESPONSE:", resp.content.decode('utf-8'))
    
    # Check if saved
    saved = Event.objects.filter(title='Test Script Event').first()
    if saved:
        print(f"SUCCESS: Event '{saved.title}' saved with ID {saved.id} and status {saved.status}")
    else:
        print("FAILURE: Event not found in database!")

if __name__ == "__main__":
    test_event_submission()
