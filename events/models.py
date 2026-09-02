import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify


class Event(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, help_text="Unique URL path")
    event_date = models.DateTimeField()
    location_name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    
    theme_settings = models.JSONField(
        default=dict, 
        blank=True, 
        help_text="Custom presentation options (primary_color, font_family, layout, page_bg_color, section_bg_color)"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    allow_plus_ones = models.BooleanField(
        default=False, 
        help_text="Allow guests to bring plus-ones"
    )
    max_plus_ones_per_guest = models.PositiveIntegerField(
        default=0, 
        help_text="Maximum number of plus-ones allowed per RSVP"
    )

    # Add this new field
    allow_guest_messages = models.BooleanField(
        default=False, 
        help_text="Allow guests to leave a special message for the celebrant"
    )

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title) or 'event'
            slug = base_slug
            counter = 1
            while Event.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.host.username})"


class RSVP(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('ATTENDING', 'Attending'),
        ('DECLINED', 'Declined'),
    ]

    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='rsvps')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    plus_ones_allowed = models.IntegerField(default=0)
    plus_ones_count = models.IntegerField(default=0)
    dietary_restrictions = models.TextField(blank=True, null=True)
    about_text = models.TextField(blank=True, null=True)  # Added for celebrant messages
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('event', 'email')

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __str__(self):
        return f"{self.full_name} - {self.event.title}"



class RSVPGuest(models.Model):
    rsvp = models.ForeignKey(RSVP, on_delete=models.CASCADE, related_name='plus_ones')
    full_name = models.CharField(max_length=255)
    dietary_restrictions = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} (Guest of {self.rsvp.first_name} {self.rsvp.last_name})"