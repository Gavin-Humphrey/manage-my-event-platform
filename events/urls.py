from django.conf import settings
from django.conf.urls.static import static
from django.urls import path
from . import views

app_name = 'events'

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('events/create/', views.create_event, name='create_event'),
    path('events/<int:pk>/edit/', views.event_form_view, name='edit_event'),
    path('e/<slug:slug>/', views.event_detail, name='event_detail'),
    path('e/<slug:slug>/rsvp/', views.submit_rsvp, name='submit_rsvp'),
    path('rsvp/<slug:slug>/', views.public_rsvp, name='public_rsvp'),
    path('dashboard/events/<slug:slug>/guests/', views.event_guests_management, name='guest_management'),
    path('dashboard/events/<slug:slug>/guests/<int:pk>/', views.view_rsvp_guest, name='view_rsvp_guest'),
    path('dashboard/events/<slug:slug>/guests/<int:pk>/edit/', views.edit_rsvp_guest, name='edit_rsvp_guest'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)