from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.urls import reverse
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


# def create_checkout_session(request, event, rsvp, tier):
#     """Creates a Stripe Checkout Session and returns the destination redirect URL."""
#     try:
#         checkout_session = stripe.checkout.Session.create(
#             payment_method_types=['card'],
#             line_items=[{
#                 'price_data': {
#                     'currency': 'usd',
#                     'product_data': {
#                         'name': f"{event.title} - {tier.name}",
#                     },
#                     'unit_amount': int(tier.price * 100),
#                 },
#                 'quantity': 1,
#             }],
#             mode='payment',
#             success_url=request.build_absolute_uri(reverse('events:rsvp_confirmed', args=[rsvp.id])) + '?session_id={CHECKOUT_SESSION_ID}',
#             cancel_url=request.build_absolute_uri(reverse('events:public_rsvp', args=[event.slug])),
#             metadata={
#                 'rsvp_id': rsvp.id,
#                 'event_id': event.id
#             }
#         )
#         return checkout_session.url
#     except stripe.error.StripeError as e:
#         print(f"Stripe Error: {e}")
#         return None

# import json
# from django.http import HttpResponse
# from django.views.decorators.csrf import csrf_exempt
# from .models import RSVP

# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
#     event = None

#     try:
#         event = stripe.Webhook.construct_event(
#             payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
#         )
#     except ValueError:
#         return HttpResponse(status=400)
#     except stripe.error.SignatureVerificationError:
#         return HttpResponse(status=400)

#     if event['type'] == 'checkout.session.completed':
#         session = event['data']['object']
#         rsvp_id = session.get('metadata', {}).get('rsvp_id')
        
#         if rsvp_id:
#             try:
#                 rsvp = RSVP.objects.get(id=rsvp_id)
#                 if not rsvp.is_paid:
#                     rsvp.is_paid = True
#                     rsvp.save()
                    
#                     # Trigger email confirmation & QR code generation
#                     # send_ticket_confirmation_email(rsvp)
#             except RSVP.DoesNotExist:
#                 pass

#     return HttpResponse(status=200)



def create_checkout_session(request, event, rsvp, tier):
    """Creates a Stripe Checkout Session and returns the destination redirect URL."""
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': f"{event.title} - {tier.name}",
                    },
                    'unit_amount': int(tier.price * 100),
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=request.build_absolute_uri(reverse('events:rsvp_confirmed', args=[rsvp.id])) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=request.build_absolute_uri(reverse('events:public_rsvp', args=[event.slug])),
            metadata={
                'rsvp_id': rsvp.id,
                'event_id': event.id
            }
        )
        return checkout_session.url
    except stripe.error.StripeError as e:
        print(f"Stripe Error: {e}")
        return None


import json
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import RSVP

@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        rsvp_id = session.get('metadata', {}).get('rsvp_id')
        
        if rsvp_id:
            try:
                rsvp = RSVP.objects.get(id=rsvp_id)
                if not rsvp.is_paid:
                    rsvp.is_paid = True
                    rsvp.save()
                    
                    if rsvp.ticket_tier:
                        rsvp.ticket_tier.sold_count += 1
                        rsvp.ticket_tier.save()
            except RSVP.DoesNotExist:
                pass

    return HttpResponse(status=200)