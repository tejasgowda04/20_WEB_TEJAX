"""Django Admin configuration for EduEvent."""
from django.contrib import admin
from core.models import (
    UserProfile, Venue, Event, EventTemplate,
    CoordinatorRequest, Notification, CollegeCalendarEntry
)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'role', 'branch', 'is_approved', 'is_active', 'created_at']
    list_filter = ['role', 'is_approved', 'is_active', 'branch']
    search_fields = ['name', 'email', 'branch']
    list_editable = ['is_approved', 'is_active']


@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'capacity', 'is_active']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'branch', 'date', 'venue', 'status', 'is_public', 'created_at']
    list_filter = ['status', 'branch', 'category', 'is_public']
    search_fields = ['title', 'branch', 'organizer']
    list_editable = ['status']


@admin.register(EventTemplate)
class EventTemplateAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'frequency', 'default_branch', 'is_active']
    list_filter = ['frequency', 'category', 'is_active']


@admin.register(CoordinatorRequest)
class CoordRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'event', 'status', 'created_at']
    list_filter = ['status']


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['message', 'user', 'target_role', 'is_read', 'created_at']
    list_filter = ['is_read', 'target_role']


@admin.register(CollegeCalendarEntry)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ['title', 'date', 'entry_type', 'is_recurring_yearly']
    list_filter = ['entry_type', 'is_recurring_yearly']
