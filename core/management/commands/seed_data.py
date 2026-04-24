"""
Seed the database with demo data: venues, users, events, calendar, templates.
Usage: python manage.py seed_data
"""
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from core.models import (
    UserProfile, Venue, Event, EventTemplate,
    CollegeCalendarEntry
)


class Command(BaseCommand):
    help = 'Seed the database with demo data'

    def handle(self, *args, **options):
        self.stdout.write('🌱 Seeding EduEvent database...\n')

        # ── Venues ──────────────────────────────────────────────
        venues_data = [
            ('V1', 'Main Auditorium', 800, 'Main hall with stage & AV system'),
            ('V2', 'Seminar Hall A', 200, 'AC seminar hall, ground floor'),
            ('V3', 'Seminar Hall B', 200, 'AC seminar hall, first floor'),
            ('V4', 'Open Ground', 2000, 'Outdoor sports & cultural ground'),
            ('V5', 'Conference Room', 50, 'Board room with projector'),
        ]
        for vid, name, cap, desc in venues_data:
            Venue.objects.get_or_create(id=vid, defaults={'name': name, 'capacity': cap, 'description': desc})
        self.stdout.write(self.style.SUCCESS(f'  ✅ {len(venues_data)} venues'))

        # ── Admin ───────────────────────────────────────────────
        admin, _ = UserProfile.objects.get_or_create(
            email='admin@college.edu',
            defaults={
                'firebase_uid': 'admin_placeholder_uid',
                'name': 'Super Admin',
                'phone': '9000000001',
                'role': 'admin',
                'branch': '',
                'is_approved': True,
                'is_active': True,
            }
        )
        self.stdout.write(self.style.SUCCESS('  ✅ Admin user'))

        # ── HODs ────────────────────────────────────────────────
        hods_data = [
            ('hod.cs@college.edu', 'Dr. Rajesh Kumar', 'Computer Science', '9100000001'),
            ('hod.it@college.edu', 'Dr. Priya Sharma', 'Information Technology', '9100000002'),
            ('hod.ec@college.edu', 'Dr. Arun Mehta', 'Electronics', '9100000003'),
            ('hod.mech@college.edu', 'Dr. Sunita Patel', 'Mechanical', '9100000004'),
        ]
        hod_objs = {}
        for email, name, branch, phone in hods_data:
            hod, _ = UserProfile.objects.get_or_create(
                email=email,
                defaults={
                    'firebase_uid': f'hod_{branch.lower().replace(" ","_")}_uid',
                    'name': name, 'phone': phone, 'role': 'hod',
                    'branch': branch, 'is_approved': True, 'is_active': True,
                    'extra_data': {'department': branch, 'designation': 'Professor & Head'},
                }
            )
            hod_objs[branch] = hod
        self.stdout.write(self.style.SUCCESS(f'  ✅ {len(hods_data)} HODs'))

        # ── Students ────────────────────────────────────────────
        students_data = [
            ('amit@student.edu', 'Amit Shah', 'Computer Science', '9200000001', 'CS21001', '2nd Year'),
            ('priya@student.edu', 'Priya Verma', 'Information Technology', '9200000002', 'IT21002', '3rd Year'),
            ('rohit@student.edu', 'Rohit Gupta', 'Electronics', '9200000003', 'EC22003', '1st Year'),
        ]
        for email, name, branch, phone, roll, year in students_data:
            UserProfile.objects.get_or_create(
                email=email,
                defaults={
                    'firebase_uid': f'stu_{roll.lower()}_uid',
                    'name': name, 'phone': phone, 'role': 'student',
                    'branch': branch, 'is_approved': True, 'is_active': True,
                    'extra_data': {'roll_no': roll, 'year': year},
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  ✅ {len(students_data)} Students'))

        # ── Teachers ────────────────────────────────────────────
        teachers_data = [
            ('anita@college.edu', 'Prof. Anita Singh', 'Computer Science', 'Data Structures'),
            ('vikas@college.edu', 'Prof. Vikas Joshi', 'Information Technology', 'Web Technology'),
            ('meena@college.edu', 'Prof. Meena Nair', 'Mechanical', 'Thermodynamics'),
        ]
        for email, name, branch, subject in teachers_data:
            UserProfile.objects.get_or_create(
                email=email,
                defaults={
                    'firebase_uid': f'tch_{name.split()[-1].lower()}_uid',
                    'name': name, 'phone': '', 'role': 'teacher',
                    'branch': branch, 'is_approved': True, 'is_active': True,
                    'extra_data': {'subject': subject, 'emp_id': ''},
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  ✅ {len(teachers_data)} Teachers'))

        # ── Events ──────────────────────────────────────────────
        today = date.today()
        events_data = [
            ('Annual Technical Symposium', 'A day-long tech symposium with paper presentations.', today + timedelta(days=7), 'V1', 'Computer Science', 'Dr. Rajesh Kumar', 'Technical', 500, 'approved'),
            ('Cultural Fest – Rangotsav', 'Annual inter-department cultural festival.', today + timedelta(days=14), 'V4', 'Information Technology', 'Dr. Priya Sharma', 'Cultural', 1200, 'approved'),
            ('Guest Lecture – AI & ML Trends', 'Expert talk on emerging AI and ML.', today + timedelta(days=3), 'V2', 'Computer Science', 'Dr. Rajesh Kumar', 'Seminar', 150, 'approved'),
            ('Robotics Workshop', 'Hands-on robotics workshop.', today - timedelta(days=10), 'V3', 'Electronics', 'Dr. Arun Mehta', 'Workshop', 120, 'approved'),
            ('Sports Day – Track Events', 'Annual sports meet.', today - timedelta(days=5), 'V4', 'Mechanical', 'Dr. Sunita Patel', 'Sports', 800, 'approved'),
            ('Entrepreneurship Summit', 'Startup pitching and mentoring.', today + timedelta(days=21), 'V5', 'MBA', 'Prof. Admin', 'Seminar', 45, 'pending'),
        ]
        for title, desc, d, vid, branch, org, cat, att, status in events_data:
            hod = hod_objs.get(branch)
            Event.objects.get_or_create(
                title=title,
                date=d,
                defaults={
                    'description': desc, 'end_date': d,
                    'venue_id': vid, 'branch': branch, 'organizer': org,
                    'hod': hod, 'category': cat, 'expected_attendees': att, 'status': status,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  ✅ {len(events_data)} Events'))

        # ── Event Templates ─────────────────────────────────────
        templates_data = [
            ('Annual Day Celebration', 'College annual day with cultural performances.', 'Cultural', 'V1', '', 1000, 'yearly', 2, 1),
            ('Fresher\'s Welcome', 'Welcome ceremony for new students.', 'Cultural', 'V4', '', 1500, 'yearly', 8, 1),
            ('Sports Meet', 'Annual inter-department sports competition.', 'Sports', 'V4', '', 2000, 'yearly', 1, 3),
            ('Tech Symposium', 'Technical paper presentations and project exhibition.', 'Technical', 'V1', 'Computer Science', 500, 'yearly', 3, 1),
            ('Guest Lecture Series', 'Monthly expert talks from industry.', 'Seminar', 'V2', '', 150, 'monthly', None, 1),
            ('Placement Training Workshop', 'Pre-placement aptitude and soft skills workshop.', 'Workshop', 'V3', '', 200, 'semesterly', None, 2),
        ]
        for title, desc, cat, vid, branch, att, freq, month, dur in templates_data:
            EventTemplate.objects.get_or_create(
                title=title,
                defaults={
                    'description': desc, 'category': cat,
                    'default_venue_id': vid, 'default_branch': branch,
                    'expected_attendees': att, 'frequency': freq,
                    'typical_month': month, 'typical_duration_days': dur,
                    'created_by': admin,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  ✅ {len(templates_data)} Event Templates'))

        # ── College Calendar ────────────────────────────────────
        year = today.year
        calendar_data = [
            ('Republic Day', date(year, 1, 26), None, 'holiday', True),
            ('Holi', date(year, 3, 14), None, 'holiday', True),
            ('Independence Day', date(year, 8, 15), None, 'holiday', True),
            ('Gandhi Jayanti', date(year, 10, 2), None, 'holiday', True),
            ('Diwali Break', date(year, 10, 20), date(year, 10, 25), 'vacation', True),
            ('Christmas', date(year, 12, 25), None, 'holiday', True),
            ('Mid-Semester Exams', date(year, 3, 1), date(year, 3, 10), 'exam', False),
            ('End-Semester Exams', date(year, 5, 1), date(year, 5, 15), 'exam', False),
            ('Summer Vacation', date(year, 5, 16), date(year, 6, 30), 'vacation', False),
            ('Semester 1 Starts', date(year, 7, 1), None, 'semester_start', False),
            ('Semester 2 Starts', date(year, 1, 2), None, 'semester_start', False),
            ('Winter Break', date(year, 12, 22), date(year, 12, 31), 'vacation', True),
        ]
        for title, d, end, etype, recurring in calendar_data:
            CollegeCalendarEntry.objects.get_or_create(
                title=title,
                date=d,
                defaults={
                    'end_date': end, 'entry_type': etype,
                    'is_recurring_yearly': recurring, 'created_by': admin,
                }
            )
        self.stdout.write(self.style.SUCCESS(f'  ✅ {len(calendar_data)} Calendar Entries'))

        self.stdout.write(self.style.SUCCESS('\n🎉 Database seeded successfully!'))
