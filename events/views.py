from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import Event, RSVP, RSVPGuest
from .forms import EventForm, RSVPForm, RSVPGuestForm
from django.utils.text import slugify
from django.db.models import Q, Sum


# -------------------------------------------------------------------
# PUBLIC & GUEST VIEWS
# -------------------------------------------------------------------

def home(request):
    return render(request, 'events/home.html')


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug)
    
    # Safely retrieve theme settings
    raw_theme = event.theme_settings() if callable(getattr(event, 'theme_settings', None)) else getattr(event, 'theme_settings', None)
    
    theme = {}
    if isinstance(raw_theme, dict):
        theme = raw_theme.copy()
        theme['theme_color'] = theme.get('theme_color') or theme.get('primary_color') or '#3b82f6'
    elif raw_theme is not None:
        theme = raw_theme

    # Normalize gallery slides and descriptions
    raw_gallery = theme.get('gallery_slides') or theme.get('gallery_images', [])
    normalized_gallery = []
    for item in raw_gallery:
        if isinstance(item, str):
            normalized_gallery.append({'url': item, 'caption': ''})
        elif isinstance(item, dict):
            url = item.get('url') or item.get('image') or ''
            caption = item.get('description') or item.get('caption') or item.get('text') or ''
            if url:
                normalized_gallery.append({'url': url, 'caption': caption})
                
    guest_messages = event.rsvps.exclude(guest_message__isnull=True).exclude(guest_message__exact='')
    
    return render(request, 'events/event_detail.html', {
        'event': event, 
        'theme': theme,
        'guest_messages': guest_messages,
        'normalized_gallery': normalized_gallery,
    })


def submit_rsvp(request, slug):
    event = get_object_or_404(Event, slug=slug)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        status = request.POST.get('status')
        plus_ones_count = int(request.POST.get('plus_ones_count', 0))
        dietary = request.POST.get('dietary_restrictions', '')

        guest, created = RSVP.objects.update_or_create(
            event=event,
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'status': status,
                'plus_ones_count': plus_ones_count,
                'dietary_restrictions': dietary,
            }
        )
        messages.success(request, f"Thank you {first_name}! Your RSVP has been recorded.")
        return redirect('event_detail', slug=slug)

    return redirect('event_detail', slug=slug)


# -------------------------------------------------------------------
# HOST AUTHENTICATION VIEWS
# -------------------------------------------------------------------

def register_host(request):
    if request.user.is_authenticated:
        #return redirect('dashboard')
        return redirect('events:dashboard')
        
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, "Account created successfully! Welcome to your dashboard.")
            #return redirect('dashboard')
            return redirect('events:dashboard')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def login_host(request):
    if request.user.is_authenticated:
        return redirect('dashboard')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'registration/register.html', {'form': form})

def logout_host(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')


# -------------------------------------------------------------------
# HOST DASHBOARD & EVENT MANAGEMENT
# -------------------------------------------------------------------

@login_required
def dashboard(request):
    events = Event.objects.filter(host=request.user).order_by('-created_at')
    
    # Global metrics across all events hosted by this user
    total_events = events.count()
    total_guests = RSVP.objects.filter(event__host=request.user).count()
    attending_guests = RSVP.objects.filter(event__host=request.user, status='ATTENDING').count()

    context = {
        'events': events,
        'total_events': total_events,
        'total_guests': total_guests,
        'attending_guests': attending_guests,
    }
    return render(request, 'events/dashboard.html', context)


@login_required
def create_event(request):
    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES)
        if form.is_valid():
            event = form.save(commit=False)
            event.host = request.user
            event.save()
            messages.success(request, f"Event '{event.title}' created successfully!")
            return redirect('events:dashboard')
    else:
        form = EventForm()
    return render(request, 'events/event_form.html', {'form': form, 'action': 'Create'})


@login_required
def edit_event(request, slug=None):
    event = get_object_or_404(Event, slug=slug)

    # Security check: ensure only the host can edit this event
    if event.host != request.user:
        messages.error(request, "You do not have permission to edit this event.")
        return redirect('events:dashboard')

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            saved_event = form.save()
            messages.success(request, f"Event '{saved_event.title}' updated successfully!")
            return redirect('events:event_detail', slug=saved_event.slug)
    else:
        form = EventForm(instance=event)

    return render(request, 'events/event_form.html', {'form': form, 'action': 'Edit'})

def event_form_view(request, pk=None):
    # Fetch existing instance if editing; otherwise, create a new one (None)
    event = get_object_or_404(Event, pk=pk) if pk else None

    if request.method == 'POST':
        form = EventForm(request.POST, request.FILES, instance=event)
        if form.is_valid():
            saved_event = form.save()
            return redirect('event_detail', pk=saved_event.pk)
    else:
        form = EventForm(instance=event)

    return render(request, 'event_form.html', {
        'form': form,
        'is_edit': event is not None
    })

# 3. PUBLIC RSVP PAGE (Guest view)

def public_rsvp(request, slug):
    event = get_object_or_404(Event, slug=slug)
    
    # Safely retrieve theme settings
    raw_theme = event.theme_settings() if callable(getattr(event, 'theme_settings', None)) else getattr(event, 'theme_settings', None)
    
    theme = {}
    if isinstance(raw_theme, dict):
        theme = raw_theme.copy()
        theme['theme_color'] = theme.get('theme_color') or theme.get('primary_color') or '#3b82f6'
    elif raw_theme is not None:
        theme = raw_theme

    # Normalize gallery slides and descriptions
    raw_gallery = theme.get('gallery_slides') or theme.get('gallery_images', [])
    normalized_gallery = []
    for item in raw_gallery:
        if isinstance(item, str):
            normalized_gallery.append({'url': item, 'caption': ''})
        elif isinstance(item, dict):
            url = item.get('url') or item.get('image') or ''
            caption = item.get('description') or item.get('caption') or item.get('text') or ''
            if url:
                normalized_gallery.append({'url': url, 'caption': caption})

    # Query RSVPs that contain a message for the carousel 
    guest_messages = event.rsvps.exclude(guest_message__isnull=True).exclude(guest_message__exact='')

    context = {
        'event': event,
        'theme': theme,
        'guest_messages': guest_messages,
        'normalized_gallery': normalized_gallery,
    }
    return render(request, 'events/public_rsvp.html', context)

def submit_rsvp(request, slug):
    event = get_object_or_404(Event, slug=slug)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        full_name = request.POST.get('full_name', '').strip()
        status = request.POST.get('status', 'ATTENDING').upper()
        guest_message = request.POST.get('guest_message', '').strip() # Capture celebrant message
        dietary_restrictions = request.POST.get('dietary_restrictions', '').strip()
        
        # Split full name into first and last name components
        name_parts = full_name.split(' ', 1)
        first_name = name_parts[0] if name_parts else ''
        last_name = name_parts[1] if len(name_parts) > 1 else ''
        
        if email and first_name:
            plus_ones_count = 0
            if status == 'ATTENDING' and event.allow_plus_ones:
                try:
                    plus_ones_count = int(request.POST.get('guest_count', 0))
                    plus_ones_count = min(plus_ones_count, event.max_plus_ones_per_guest)
                except ValueError:
                    plus_ones_count = 0

            rsvp, created = RSVP.objects.update_or_create(
                event=event,
                email=email,
                defaults={
                    'first_name': first_name,
                    'last_name': last_name,
                    'status': status,
                    'plus_ones_allowed': getattr(event, 'max_plus_ones_per_guest', 0),
                    'plus_ones_count': plus_ones_count,
                    'guest_message': guest_message, # Save the message here
                    'dietary_restrictions': dietary_restrictions,
                }
            )

            # Clear old plus-ones if updating, then insert fresh individual names
            if hasattr(rsvp, 'plus_ones'):
                rsvp.plus_ones.all().delete()
                if status == 'ATTENDING' and event.allow_plus_ones:
                    for i in range(1, plus_ones_count + 1):
                        # Match HTML template loop name: 'guest_name_i'
                        guest_name = request.POST.get(f'guest_name_{i}')
                        if guest_name:
                            RSVPGuest.objects.create(
                                rsvp=rsvp,
                                full_name=guest_name
                            )

            messages.success(request, "Your RSVP has been recorded successfully!")
        else:
            messages.error(request, "Email and Full Name are required fields.")
            
    return redirect('events:public_rsvp', slug=event.slug)

@login_required
def event_rsvps_management(request, slug):
    event = get_object_or_404(Event, slug=slug, host=request.user)
    rsvps = event.rsvps.all()
    
    search_query = request.GET.get('q', '').strip()
    if search_query:
        rsvps = rsvps.filter(
            Q(first_name__icontains=search_query) |
            Q(last_name__icontains=search_query) |
            Q(email__icontains=search_query)
        )
        
    status_filter = request.GET.get('status', '').strip()
    if status_filter:
        rsvps = rsvps.filter(status=status_filter)

    total_rsvps = event.rsvps.count()
    attending_count = event.rsvps.filter(status='ATTENDING').count()
    
    # Calculate total headcount including primary RSVPs plus their plus-ones
    total_headcount = attending_count
    extra = event.rsvps.filter(status='ATTENDING').aggregate(
        total=Sum('plus_ones_count', default=0)
    )['total']
    total_headcount += (extra or 0)

    context = {
        'event': event,
        'rsvps': rsvps,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_rsvps': total_rsvps,
        'attending_count': attending_count,
        'total_headcount': total_headcount,
    }
    return render(request, 'events/event_rsvps_management.html', context)


def view_rsvp_detail(request, slug, pk):
    event = get_object_or_404(Event, slug=slug)
    rsvp = get_object_or_404(RSVP, pk=pk, event=event)
    
    context = {
        'event': event,
        'rsvp': rsvp,
        'additional_guests': rsvp.plus_ones.all(),
    }
    return render(request, 'events/view_rsvp_detail.html', context)


def edit_rsvp(request, slug, pk):
    event = get_object_or_404(Event, slug=slug)
    rsvp = get_object_or_404(RSVP, pk=pk, event=event)
    
    if request.method == 'POST':
        form = RSVPForm(request.POST, instance=rsvp)
        if form.is_valid():
            updated_rsvp = form.save(commit=False)
            
            # Handle guest count & dynamic plus-one names correctly using RSVPGuest
            if event.allow_plus_ones and event.max_plus_ones_per_guest > 0:
                try:
                    guest_count = int(request.POST.get('guest_count', 0))
                except ValueError:
                    guest_count = 0
                
                if guest_count > event.max_plus_ones_per_guest:
                    guest_count = event.max_plus_ones_per_guest
                if guest_count < 0:
                    guest_count = 0
                
                updated_rsvp.plus_ones_count = guest_count
                updated_rsvp.save()
                
                # Clear and recreate plus-ones using RSVPGuest model
                rsvp.plus_ones.all().delete()
                for i in range(1, guest_count + 1):
                    guest_name = request.POST.get(f'plus_one_name_{i}')
                    if guest_name:
                        RSVPGuest.objects.create(rsvp=updated_rsvp, full_name=guest_name)
            else:
                updated_rsvp.save()
                
            return redirect('events:view_rsvp_detail', slug=event.slug, pk=rsvp.pk)
    else:
        form = RSVPForm(instance=rsvp)
        
    context = {
        'event': event,
        'rsvp': rsvp,
        'form': form,
    }
    return render(request, 'events/edit_rsvp.html', context)
