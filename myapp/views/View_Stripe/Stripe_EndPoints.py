

import stripe
import time
import logging
import json
import requests
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.shortcuts import render
import os
from dotenv import load_dotenv
from datetime import datetime
from django.db.models import Q

# Import your models
from myapp.model.roller_booking_model import RollerBookingDetails
from myapp.utils.roller_token_manager import get_or_refresh_roller_token
from myapp.utils.send_email import send_booking_confirmation_email

load_dotenv()

logger = logging.getLogger(__name__)


def get_booking_for_payment(booking_id):
    """
    Get booking for payment webhook, handling multiple bookings
    """
    try:
        # First, get all bookings with this external_id that are not paid
        bookings = RollerBookingDetails.objects.filter(
            Q(external_id=booking_id) | 
            Q(booking_unique_id=booking_id)
        ).filter(
            is_booking_paid=False,
            booking_status='live'
        ).order_by('-creation_date')
        
        if bookings.exists():
            if bookings.count() > 1:
                logger.warning(f"Multiple unpaid bookings found for {booking_id}, using most recent")
            return bookings.first()
        
        # If no unpaid bookings, try to find any booking with this ID
        bookings = RollerBookingDetails.objects.filter(
            Q(external_id=booking_id) | 
            Q(booking_unique_id=booking_id)
        ).order_by('-creation_date')
        
        if bookings.exists():
            return bookings.first()
        
        return None
        
    except Exception as e:
        logger.error(f"Error finding booking for payment {booking_id}: {str(e)}")
        return None


def add_transaction_to_roller(booking, session_data):
    """
    Call Roller API to add transaction record for the booking
    """
    try:
        # Get the Roller booking uniqueId from the booking
        roller_booking_id = None
        
        # First try to get from roller_booking_id field (should be populated now)
        if hasattr(booking, 'roller_booking_id') and booking.roller_booking_id:
            roller_booking_id = booking.roller_booking_id
        
        # If not, try payload
        if not roller_booking_id:
            try:
                payload_data = booking.payload
                if isinstance(payload_data, str):
                    payload_data = json.loads(payload_data)
                
                # Look for roller booking ID in various possible keys
                roller_booking_id = payload_data.get('roller_response', {}).get('uniqueId')
                if not roller_booking_id:
                    roller_booking_id = payload_data.get('roller_booking_id')
                if not roller_booking_id:
                    roller_booking_id = payload_data.get('uniqueId')
            except Exception as e:
                logger.error(f"Error parsing payload: {str(e)}")
        
        if not roller_booking_id:
            logger.error(f"No Roller booking ID found for booking {booking.external_id}")
            
            # Log debug info
            logger.info(f"Booking details: external_id={booking.external_id}, booking_unique_id={booking.booking_unique_id}")
            if hasattr(booking, 'roller_booking_id'):
                logger.info(f"roller_booking_id field: {booking.roller_booking_id}")
            
            return False
        
        # Get location to obtain API token
        if not hasattr(booking, 'location_id') or not booking.location_id:
            logger.error(f"No location associated with booking {booking.external_id}")
            return False
        
        # Get the token for this location
        access_token = get_or_refresh_roller_token(booking.location_id)
        print("This is the access Token ==")
        if not access_token:
            logger.error(f"Failed to get Roller API token for location {booking.location_id.location_name}")
            return False
        
        # Prepare payment data for Roller API
        deposit_amount = session_data.get('amount_total', 0) / 100  # Convert from cents to dollars
        
        # Create a unique transaction ID (using Stripe payment intent if available)
        transaction_id = session_data.get('payment_intent', '')
        if not transaction_id:
            # Generate a unique ID
            transaction_id = f"STRIPE_{int(time.time())}_{booking.external_id}"
        
        # Prepare the request payload
        roller_payload = {
            "id": transaction_id,
            "paymentType": "CreditCard",
            "amount": float(deposit_amount),
            "creditCardFees": 0,  # You can calculate this if needed
            "transactionDate": datetime.utcnow().isoformat() + "Z"
        }
        
        logger.info(f"Calling Roller API for booking {roller_booking_id} with payload: {roller_payload}")
        
        # Make API call to Roller
        roller_api_url = f"https://api.haveablast.roller.app/bookings/{roller_booking_id}/payments"
        
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        response = requests.post(
            roller_api_url,
            json=roller_payload,
            headers=headers,
            timeout=30
        )
        
        if response.status_code == 201:
            result = response.json()
            logger.info(f"Successfully added transaction to Roller for booking {roller_booking_id}")
            
            # Update booking with Roller transaction info
            try:
                payload_data = booking.payload
                if isinstance(payload_data, str):
                    payload_data = json.loads(payload_data)
                
                if not isinstance(payload_data, dict):
                    payload_data = {}
                
                # Add Roller transaction info
                if 'roller_transactions' not in payload_data:
                    payload_data['roller_transactions'] = []
                
                payload_data['roller_transactions'].append({
                    'transaction_id': transaction_id,
                    'roller_payment_id': result.get('uniqueId'),
                    'amount': deposit_amount,
                    'added_at': datetime.utcnow().isoformat(),
                    'status': 'success'
                })
                
                booking.payload = json.dumps(payload_data)
                booking.save(update_fields=['payload'])
                
            except Exception as e:
                logger.error(f"Error updating payload with Roller transaction info: {str(e)}")
            
            return True
        elif response.status_code == 409:
            logger.warning(f"Transaction already exists in Roller for booking {roller_booking_id}")
            return True
        else:
            logger.error(f"Failed to add transaction to Roller. Status: {response.status_code}, Response: {response.text}")
            return False
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error calling Roller API: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error in add_transaction_to_roller: {str(e)}", exc_info=True)
        return False


# @csrf_exempt
# def stripe_webhook(request):
#     payload = request.body
#     sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

#     try:
#         event = stripe.Webhook.construct_event(
#             payload,
#             sig_header,
#             os.getenv("STRIPE_WEBHOOK_SECRET_key")
#         )
#     except stripe.error.SignatureVerificationError:
#         return HttpResponse(status=400)

#     event_type = event["type"]
#     session = event["data"]["object"]
#     logger.info(f"Stripe webhook received: {event_type}")
    
#     if event_type == "checkout.session.completed":
#         if session["payment_status"] == "paid":
#             booking_id = session["client_reference_id"]
#             deposit_cents = int(session["metadata"]["deposit_amount_cents"])
#             deposit_dollars = deposit_cents / 100
            
#             # Get the booking (handles multiple bookings)
#             booking = get_booking_for_payment(booking_id)
            
#             if booking:
#                 logger.info(f"Found booking for webhook: {booking.external_id} (DB ID: {booking.booking_id})")
                
#                 # Call Roller API to add transaction
#                 roller_success = add_transaction_to_roller(booking, session)
                
#                 if roller_success:
#                     logger.info(f"Successfully added transaction to Roller for booking {booking.external_id}")
#                 else:
#                     logger.warning(f"Failed to add transaction to Roller for booking {booking.external_id}")
                
#                 # Update booking as paid
#                 mark_booking_paid(booking, deposit_dollars, session)
#                 logger.info(f"Booking {booking.external_id} marked as paid. Deposit: ${deposit_dollars}")
#             else:
#                 logger.error(f"No booking found for webhook: {booking_id}")

#     elif event_type == "checkout.session.expired":
#         booking_id = session.get("client_reference_id")
        
#         # Get the booking
#         booking = get_booking_for_payment(booking_id)
#         if booking:
#             mark_booking_expired(booking, session)
#             logger.info(f"Booking {booking.external_id} marked as expired/cancelled")
#         else:
#             logger.error(f"No booking found for expired webhook: {booking_id}")

#     return HttpResponse(status=200)



@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")

    try:
        event = stripe.Webhook.construct_event(
            payload,
            sig_header,
            os.getenv("STRIPE_WEBHOOK_SECRET_key")
        )
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    event_type = event["type"]
    session = event["data"]["object"]
    logger.info(f"Stripe webhook received: {event_type}")
    
    if event_type == "checkout.session.completed":
        if session["payment_status"] == "paid":
            booking_id = session["client_reference_id"]
            deposit_cents = int(session["metadata"]["deposit_amount_cents"])
            deposit_dollars = deposit_cents / 100
            
            # Get total amount from session
            total_amount_cents = session.get("amount_total", 0)
            total_amount_dollars = total_amount_cents / 100
            
            # Get the booking (handles multiple bookings)
            booking = get_booking_for_payment(booking_id)
            
            if booking:
                logger.info(f"Found booking for webhook: {booking.external_id} (DB ID: {booking.booking_id})")
                
                # Call Roller API to add transaction
                roller_success = add_transaction_to_roller(booking, session)
                
                if roller_success:
                    logger.info(f"Successfully added transaction to Roller for booking {booking.external_id}")
                else:
                    logger.warning(f"Failed to add transaction to Roller for booking {booking.external_id}")
                
                # Update booking as paid
                mark_booking_paid(booking, deposit_dollars, session)
                logger.info(f"Booking {booking.external_id} marked as paid. Deposit: ${deposit_dollars}")
                
                # Send confirmation email
                try:
                    logger.info(f"Attempting to send confirmation email for booking {booking.external_id}")
                    
                    # Call the email function
                    email_sent = send_booking_confirmation_email(
                        booking=booking,
                        stripe_session=session,
                        deposit_amount=deposit_dollars,
                        total_amount=total_amount_dollars
                    )
                    
                    if email_sent:
                        logger.info(f"Confirmation email sent successfully for booking {booking.external_id}")
                        
                        # Update booking payload with email info
                        try:
                            payload_data = booking.payload
                            if isinstance(payload_data, str):
                                payload_data = json.loads(payload_data)
                            
                            if not isinstance(payload_data, dict):
                                payload_data = {}
                            
                            # Add email info to payload
                            payload_data['confirmation_email'] = {
                                'sent_at': datetime.now().isoformat(),
                                'customer_email': session.get('customer_details', {}).get('email'),
                                'status': 'sent'
                            }
                            
                            booking.payload = json.dumps(payload_data)
                            booking.save(update_fields=['payload'])
                        except Exception as e:
                            logger.error(f"Error updating booking with email info: {str(e)}")
                    
                    else:
                        logger.error(f"Failed to send confirmation email for booking {booking.external_id}")
                        
                        # Update booking payload with email failure
                        try:
                            payload_data = booking.payload
                            if isinstance(payload_data, str):
                                payload_data = json.loads(payload_data)
                            
                            if not isinstance(payload_data, dict):
                                payload_data = {}
                            
                            payload_data['confirmation_email'] = {
                                'attempted_at': datetime.now().isoformat(),
                                'status': 'failed'
                            }
                            
                            booking.payload = json.dumps(payload_data)
                            booking.save(update_fields=['payload'])
                        except Exception as e:
                            logger.error(f"Error updating booking with email failure info: {str(e)}")
                            
                except Exception as e:
                    logger.error(f"Error in email sending process for booking {booking.external_id}: {str(e)}")
            else:
                logger.error(f"No booking found for webhook: {booking_id}")

    elif event_type == "checkout.session.expired":
        booking_id = session.get("client_reference_id")
        
        # Get the booking
        booking = get_booking_for_payment(booking_id)
        if booking:
            mark_booking_expired(booking, session)
            logger.info(f"Booking {booking.external_id} marked as expired/cancelled")
        else:
            logger.error(f"No booking found for expired webhook: {booking_id}")

    return HttpResponse(status=200)



def mark_booking_paid(booking, deposit_amount, session_data=None):
    """
    Update booking when payment is successful
    """
    try:
        booking.booking_status = "paid"
        booking.deposit_made_in_doller = deposit_amount
        booking.payment_made = True
        booking.is_booking_paid = True
        
        # Update payload with payment info
        try:
            payload_data = booking.payload
            if isinstance(payload_data, str):
                payload_data = json.loads(payload_data)
            
            if not isinstance(payload_data, dict):
                payload_data = {}
            
            # Add payment info to payload
            if session_data:
                payload_data['stripe_payment'] = {
                    'session_id': session_data.get('id'),
                    'payment_intent': session_data.get('payment_intent'),
                    'payment_status': session_data.get('payment_status'),
                    'amount_paid': deposit_amount,
                    'paid_at': datetime.utcnow().isoformat(),
                    'customer_email': session_data.get('customer_details', {}).get('email')
                }
            
            booking.payload = json.dumps(payload_data)
        except Exception as e:
            logger.error(f"Error updating payload with payment info: {str(e)}")
        
        booking.save()
        logger.info(f"Successfully updated booking {booking.external_id} as paid")
        return True
    except Exception as e:
        logger.error(f"Error updating booking {booking.external_id if booking else 'Unknown'}: {str(e)}", exc_info=True)
        return False


def mark_booking_expired(booking, session_data=None):
    """
    Update booking when payment link expires
    """
    try:
        booking.booking_status = "cancelled"
        booking.is_booking_paid = False
        
        # Update payload with expiration info
        try:
            payload_data = booking.payload
            if isinstance(payload_data, str):
                payload_data = json.loads(payload_data)
            
            if not isinstance(payload_data, dict):
                payload_data = {}
            
            # Add expiration info to payload
            if session_data:
                payload_data['stripe_expiration'] = {
                    'session_id': session_data.get('id'),
                    'expired_at': datetime.utcnow().isoformat(),
                    'status': 'expired'
                }
            
            booking.payload = json.dumps(payload_data)
        except Exception as e:
            logger.error(f"Error updating payload with expiration info: {str(e)}")
        
        booking.save()
        logger.info(f"Successfully updated booking {booking.external_id} as expired/cancelled")
        return True
    except Exception as e:
        logger.error(f"Error updating booking {booking.external_id if booking else 'Unknown'}: {str(e)}")
        return False


class PaymentSuccess(APIView):
    """
    HTML view for successful payment redirect
    """
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.GET.get("session_id")
        
        if not session_id:
            return render(request, 'payment_error.html', {
                'error_message': 'No session ID provided'
            })
        
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.status == "expired":
                return render(request, 'payment_expired.html')
            
            if session.payment_status == "paid":
                # Get booking details for display
                booking_id = session.get("client_reference_id")
                
                # Try to find booking
                booking = get_booking_for_payment(booking_id)
                
                if booking:
                    deposit_amount = booking.deposit_made_in_doller or 0
                    booking_status = booking.booking_status
                else:
                    deposit_amount = 0
                    booking_status = "unknown"
                
                return render(request, 'payment_success.html', {
                    'booking_id': booking_id,
                    'deposit_amount': deposit_amount,
                    'booking_status': booking_status,
                    'customer_email': session.get('customer_details', {}).get('email', '')
                })
            
            return render(request, 'payment_pending.html')
            
        except Exception as e:
            logger.error(f"Error in PaymentSuccess view: {str(e)}")
            return render(request, 'payment_error.html', {
                'error_message': str(e)
            })


class PaymentExpired(APIView):
    """
    HTML view for expired payment link
    """
    permission_classes = [AllowAny]

    def get(self, request):
        return render(request, 'payment_expired.html')

