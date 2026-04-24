"""
EduEvent – Database Models
All models for users, events, venues, calendar, templates, notifications, public wall.
"""
import uuid
from django.db import models
from django.utils import timezone


# ═══════════════════════════════════════════════════════════════════
# USER PROFILES (linked to Firebase UID)
# ═══════════════════════════════════════════════════════════════════

class UserProfile(models.Model):
    """Base user profile linked to Firebase Auth UID."""
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hod', 'HOD'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    firebase_uid = models.CharField(max_length=128, unique=True, db_index=True)
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=200)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    branch = models.CharField(max_length=100, blank=True)
    is_approved = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # Role-specific fields stored as JSON
    extra_data = models.JSONField(default=dict, blank=True)
    # For students: { "roll_no": "CS21001", "year": "2nd Year" }
    # For HOD: { "department": "...", "designation": "..." }
    # For teachers: { "subject": "...", "emp_id": "..." }

    # Email notification preferences
    email_notifications = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_profiles'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.role} - {self.branch})"

    @property
    def initials(self):
        parts = self.name.split()
        return ''.join(p[0].upper() for p in parts[:2])


# ═══════════════════════════════════════════════════════════════════
# VENUES
# ═══════════════════════════════════════════════════════════════════

class Venue(models.Model):
    """College venues for events."""
    id = models.CharField(max_length=10, primary_key=True)
    name = models.CharField(max_length=200)
    capacity = models.PositiveIntegerField(default=100)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'venues'
        ordering = ['name']

    def __str__(self):
        return f"{self.name} (Cap: {self.capacity})"


# ═══════════════════════════════════════════════════════════════════
# EVENT TEMPLATES (recurring / default templates)
# ═══════════════════════════════════════════════════════════════════

class EventTemplate(models.Model):
    """Templates for events that happen regularly (every year, semester, etc.)."""
    FREQUENCY_CHOICES = [
        ('yearly', 'Yearly'),
        ('semesterly', 'Every Semester'),
        ('monthly', 'Monthly'),
        ('one_time', 'One Time'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField()
    category = models.CharField(max_length=50, default='Other')
    default_venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True)
    default_branch = models.CharField(max_length=100, blank=True)
    expected_attendees = models.PositiveIntegerField(default=100)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='yearly')
    typical_month = models.PositiveSmallIntegerField(null=True, blank=True, help_text='1-12 for typical scheduling month')
    typical_duration_days = models.PositiveSmallIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'event_templates'
        ordering = ['title']

    def __str__(self):
        return f"[TPL] {self.title} ({self.get_frequency_display()})"


# ═══════════════════════════════════════════════════════════════════
# EVENTS
# ═══════════════════════════════════════════════════════════════════

class Event(models.Model):
    """Main event model."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    CATEGORY_CHOICES = [
        ('Technical', 'Technical'),
        ('Cultural', 'Cultural'),
        ('Sports', 'Sports'),
        ('Seminar', 'Seminar'),
        ('Workshop', 'Workshop'),
        ('Other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    description = models.TextField()
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE, related_name='events')
    branch = models.CharField(max_length=100)
    organizer = models.CharField(max_length=200)
    hod = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='submitted_events')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    expected_attendees = models.PositiveIntegerField(default=100)
    admin_note = models.TextField(blank=True)

    # Suggestion fields
    suggested_date = models.DateField(null=True, blank=True)
    suggested_venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, null=True, blank=True, related_name='suggested_events')

    # Template link (if created from template)
    template = models.ForeignKey(EventTemplate, on_delete=models.SET_NULL, null=True, blank=True)

    # Public event fields
    is_public = models.BooleanField(default=False)
    public_slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
    public_description = models.TextField(blank=True, help_text='Extra info shown on public page')
    registration_link = models.URLField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'events'
        ordering = ['date']

    def __str__(self):
        return f"{self.title} ({self.date}) - {self.status}"

    @property
    def venue_name(self):
        return self.venue.name if self.venue else '—'

    @property
    def is_past(self):
        return self.date < timezone.now().date()

    @property
    def is_upcoming(self):
        return self.date >= timezone.now().date()

    def save(self, *args, **kwargs):
        if not self.end_date:
            self.end_date = self.date
        # Auto-generate public slug
        if self.is_public and not self.public_slug:
            from django.utils.text import slugify
            base = slugify(self.title)[:60]
            self.public_slug = f"{base}-{uuid.uuid4().hex[:8]}"
        super().save(*args, **kwargs)


# ═══════════════════════════════════════════════════════════════════
# COORDINATOR REQUESTS
# ═══════════════════════════════════════════════════════════════════

class CoordinatorRequest(models.Model):
    """Students apply to be coordinators for events."""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='coord_requests')
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='coord_requests')
    hod = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='coord_approvals')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'coordinator_requests'
        unique_together = ['student', 'event']
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.student.name} → {self.event.title} ({self.status})"


# ═══════════════════════════════════════════════════════════════════
# NOTIFICATIONS
# ═══════════════════════════════════════════════════════════════════

class Notification(models.Model):
    """In-app notification system."""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    target_role = models.CharField(max_length=10, blank=True, help_text='Broadcast to all users of this role')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    link = models.CharField(max_length=500, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'notifications'
        ordering = ['-created_at']

    def __str__(self):
        target = self.user.name if self.user else f"Role:{self.target_role}"
        return f"[{target}] {self.message[:60]}"


# ═══════════════════════════════════════════════════════════════════
# COLLEGE CALENDAR
# ═══════════════════════════════════════════════════════════════════

class CollegeCalendarEntry(models.Model):
    """College calendar: holidays, exams, semester dates, etc."""
    TYPE_CHOICES = [
        ('holiday', 'Holiday'),
        ('exam', 'Examination'),
        ('semester_start', 'Semester Start'),
        ('semester_end', 'Semester End'),
        ('vacation', 'Vacation'),
        ('event', 'College Event'),
        ('other', 'Other'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=300)
    date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    entry_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='other')
    description = models.TextField(blank=True)
    is_recurring_yearly = models.BooleanField(default=False)
    created_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'college_calendar'
        ordering = ['date']
        verbose_name_plural = 'College Calendar Entries'

    def __str__(self):
        return f"[{self.get_entry_type_display()}] {self.title} ({self.date})"
