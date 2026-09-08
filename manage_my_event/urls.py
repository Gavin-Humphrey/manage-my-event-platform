"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from events import views as event_views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Global Auth Routes
    #path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path(
        'login/',
        auth_views.LoginView.as_view(
            next_page='events:dashboard'
        ),
        name='login',
    ),
    path('logout/', event_views.logout_host, name='logout'),
    path('register/', event_views.register_host, name='register'),
    
    # App-specific Routes
    path('', include('events.urls')),

    path('cookies/', event_views.event_cookies, name='cookies'),
    path('privacy/', event_views.event_privacy, name='privacy'),
    path('terms/', event_views.event_terms, name='terms'),


    path('conference/', event_views.conference, name='conference'),
    path('gig/', event_views.gig, name='gig'),
    path('live_stream/', event_views.live_stream, name='live_stream'),
    path('private_event/', event_views.private_event, name='private_event'),
    path('summit/', event_views.summit, name='summit'),
]
