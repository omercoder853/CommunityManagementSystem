from django.contrib import admin
from .models import (
    CustomUser, Community, CommunityRequest,
    Member, JoinRequest, Staff, Event, Announcement
)


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'get_full_name', 'email', 'role', 'department']
    list_filter = ['role']
    search_fields = ['username', 'email', 'first_name', 'last_name']


@admin.register(Community)
class CommunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'director', 'advisor', 'founded_date', 'is_active']
    list_filter = ['is_active']
    search_fields = ['name']


@admin.register(CommunityRequest)
class CommunityRequestAdmin(admin.ModelAdmin):
    list_display = ['community_name', 'requester', 'advisor', 'status', 'created_at']
    list_filter = ['status']


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['student', 'community', 'joined_date']


@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    list_display = ['student', 'community', 'status', 'created_at']
    list_filter = ['status']


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ['student', 'community', 'task', 'assigned_date']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'community', 'event_date', 'location_type', 'is_active']
    list_filter = ['is_active', 'location_type']


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ['title', 'community', 'created_by', 'created_at', 'is_global']
    list_filter = ['is_global']
