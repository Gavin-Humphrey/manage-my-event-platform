from django.conf import settings
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_rsvp_confirmation(rsvp):
    event = rsvp.event
    subject = f"Confirmation: You're attending {event.title}!"
    
    theme = getattr(event, 'theme', None)
    style_card_bg = getattr(theme, 'card_bg', '#ffffff') if theme else '#ffffff'
    style_body = getattr(theme, 'body_color', '#334155') if theme else '#334155'
    style_muted = getattr(theme, 'muted_color', '#64748b') if theme else '#64748b'
    
    context = {
        'rsvp': rsvp,
        'event': event,
        'style_card_bg': style_card_bg,
        'style_body': style_body,
        'style_muted': style_muted,
    }
    
    html_message = render_to_string('events/emails/rsvp_confirmation.html', context)
    plain_message = strip_tags(html_message)
    
    email = EmailMultiAlternatives(
        subject=subject,
        body=plain_message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[rsvp.email]
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=False)
    
    rsvp.confirmation_sent = True
    rsvp.save(update_fields=['confirmation_sent'])