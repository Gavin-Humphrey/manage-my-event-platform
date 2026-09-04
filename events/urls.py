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
    # path('events/<slug:slug>/edit/', views.edit_event, name='edit_event'),
    path('dashboard/events/<slug:slug>/edit/', views.edit_event, name='edit_event'),
    path('e/<slug:slug>/rsvp/', views.submit_rsvp, name='submit_rsvp'),
    path('rsvp/<slug:slug>/', views.public_rsvp, name='public_rsvp'),
    path('dashboard/events/<slug:slug>/guests/', views.event_rsvps_management, name='event_rsvps_management'),
    path('dashboard/events/<slug:slug>/guests/<int:pk>/', views.view_rsvp_detail, name='view_rsvp_detail'),
    path('dashboard/events/<slug:slug>/guests/<int:pk>/edit/', views.edit_rsvp, name='edit_rsvp'),

    path('dashboard/events/<slug:slug>/clone/', views.clone_event, name='clone_event'),

    path('e/<slug:slug>/calendar/ics/', views.download_ics, name='download_ics'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)