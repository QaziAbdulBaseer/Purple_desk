"""
Stripe webhook utility functions
"""

import logging
import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.views import View
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from dotenv import load_dotenv
load_dotenv()
import os

logger = logging.getLogger(__name__)

class StripeWebhookUtils:
    """Utility class for Stripe webhook operations"""
    
    @staticmethod
    @csrf_exempt
    def handle_webhook(request):
        """
        Handle Stripe webhook events
        
        Args:
            request: Django HTTP request
            
        Returns:
            HTTP response
        """
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
        # print("this is setting data === " , settings.STRIPE_WEBHOOK_SECRET)
        print("ok")
        try:
            event = stripe.Webhook.construct_event(
                payload,
                sig_header,
                os.getenv(STRIPE_WEBHOOK_SECRET_key)
            )
        except ValueError as e:
            logger.error(f"Invalid payload: {str(e)}")
            return HttpResponse(status=400)
        except stripe.error.SignatureVerificationError as e:
            logger.error(f"Invalid signature: {str(e)}")
            return HttpResponse(status=400)
        
        # Handle the event
        event_type = event["type"]
        session = event["data"]["object"]
        
        logger.info(f"Received Stripe webhook event: {event_type}")
        
        if event_type == "checkout.session.completed":
            return StripeWebhookUtils._handle_session_completed(session)
        elif event_type == "checkout.session.expired":
            return StripeWebhookUtils._handle_session_expired(session)
        elif event_type == "payment_intent.succeeded":
            return StripeWebhookUtils._handle_payment_succeeded(session)
        elif event_type == "payment_intent.payment_failed":
            return StripeWebhookUtils._handle_payment_failed(session)
        else:
            logger.info(f"Unhandled event type: {event_type}")
        
        return HttpResponse(status=200)
    
    @staticmethod
    def _handle_session_completed(session):
        """Handle checkout.session.completed event"""
        try:
            if session["payment_status"] == "paid":
                booking_id = session.get("client_reference_id")
                metadata = session.get("metadata", {})
                
                logger.info(f"Payment completed for booking: {booking_id}")
                
                # Extract payment details
                deposit_cents = int(metadata.get("deposit_amount_cents", 0))
                booking_id = metadata.get("booking_id")
                booking_unique_id = metadata.get("booking_unique_id")
                
                # TODO: Update booking status in database
                # mark_booking_paid_if_not_already(booking_id, deposit_cents)
                
                logger.info(f"Payment successful for booking {booking_unique_id}: ${deposit_cents/100}")
            
            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Error handling session completed: {str(e)}")
            return HttpResponse(status=500)
    
    @staticmethod
    def _handle_session_expired(session):
        """Handle checkout.session.expired event"""
        try:
            booking_id = session.get("client_reference_id")
            metadata = session.get("metadata", {})
            booking_unique_id = metadata.get("booking_unique_id")
            
            logger.warning(f"Payment session expired for booking: {booking_unique_id}")
            
            # TODO: Mark booking as expired/unpaid
            # mark_booking_expired(booking_id)
            
            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Error handling session expired: {str(e)}")
            return HttpResponse(status=500)
    
    @staticmethod
    def _handle_payment_succeeded(payment_intent):
        """Handle payment_intent.succeeded event"""
        try:
            # This is a backup handler for payment success
            logger.info(f"Payment intent succeeded: {payment_intent.get('id')}")
            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Error handling payment succeeded: {str(e)}")
            return HttpResponse(status=500)
    
    @staticmethod
    def _handle_payment_failed(payment_intent):
        """Handle payment_intent.payment_failed event"""
        try:
            logger.warning(f"Payment intent failed: {payment_intent.get('id')}")
            return HttpResponse(status=200)
        except Exception as e:
            logger.error(f"Error handling payment failed: {str(e)}")
            return HttpResponse(status=500)


# class PaymentSuccessView(APIView):
#     """API view to handle payment success callback"""
#     permission_classes = [AllowAny]
    
#     def get(self, request):
#         """
#         Handle payment success redirect
        
#         Query Params:
#             session_id: Stripe session ID
#         """
#         session_id = request.GET.get("session_id")
        
#         if not session_id:
#             return Response({
#                 "success": False,
#                 "message": "session_id is required"
#             }, status=400)
        
#         try:
#             # Import here to avoid circular dependency
#             from myapp.utils.stripe_utils import StripePaymentUtils
            
#             session_info = StripePaymentUtils.retrieve_session(session_id)
            
#             if not session_info.get("success"):
#                 return Response({
#                     "success": False,
#                     "message": "Invalid session ID",
#                     "error": session_info.get("error")
#                 }, status=400)
            
#             if session_info.get("status") == "expired":
#                 return Response({
#                     "success": False,
#                     "message": "Payment link expired",
#                     "payment_status": "expired"
#                 }, status=400)
            
#             if session_info.get("payment_status") == "paid":
#                 return Response({
#                     "success": True,
#                     "message": "Payment completed successfully",
#                     "payment_status": "paid",
#                     "session_id": session_info.get("session_id"),
#                     "amount": session_info.get("amount_total") / 100 if session_info.get("amount_total") else 0,
#                     "currency": session_info.get("currency"),
#                     "metadata": session_info.get("metadata")
#                 })
            
#             return Response({
#                 "success": False,
#                 "message": "Payment not completed",
#                 "payment_status": session_info.get("payment_status"),
#                 "session_status": session_info.get("status")
#             }, status=400)
            
#         except Exception as e:
#             logger.error(f"Error in payment success view: {str(e)}")
#             return Response({
#                 "success": False,
#                 "message": "Error verifying payment status",
#                 "error": str(e)
#             }, status=500)



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
                    total_amount = session.get('amount_total', 0) / 100
                    
                    # Check if email was already sent
                    try:
                        payload_data = booking.payload
                        if isinstance(payload_data, str):
                            payload_data = json.loads(payload_data)
                        
                        email_sent = payload_data.get('confirmation_email', {}).get('status') == 'sent'
                        
                        # If email not sent yet, send it (this is a backup in case webhook failed)
                        if not email_sent:
                            logger.info(f"Email not sent yet for booking {booking_id}, attempting to send from success page")
                            send_booking_confirmation_email(
                                booking=booking,
                                stripe_session=session,
                                deposit_amount=deposit_amount,
                                total_amount=total_amount
                            )
                    except:
                        pass
                    
                    return render(request, 'payment_success.html', {
                        'booking_id': booking_id,
                        'deposit_amount': deposit_amount,
                        'total_amount': total_amount,
                        'booking_status': booking_status,
                        'customer_email': session.get('customer_details', {}).get('email', ''),
                        'confirmation_sent': True
                    })
                else:
                    return render(request, 'payment_error.html', {
                        'error_message': 'Booking not found'
                    })
            
            return render(request, 'payment_pending.html')
            
        except Exception as e:
            logger.error(f"Error in PaymentSuccess view: {str(e)}")
            return render(request, 'payment_error.html', {
                'error_message': str(e)
            })


