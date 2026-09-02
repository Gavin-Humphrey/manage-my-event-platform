from django.contrib import admin
from .models import Event, RSVP, RSVPGuest


class GuestInline(admin.TabularInline):
    model = RSVP
    extra = 1


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'event_date', 'slug', 'created_at')
    search_fields = ('title', 'host__username', 'slug')
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GuestInline]

@admin.register(RSVP)
class GuestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'event', 'status', 'plus_ones_count', 'dietary_restrictions', 'about_text')
    list_filter = ('status', 'event')
    search_fields = ('first_name', 'last_name', 'email', 'event__title')
    list_per_page = 25