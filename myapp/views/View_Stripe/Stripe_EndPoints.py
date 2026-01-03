






import stripe
import time

from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
import os
from dotenv import load_dotenv
load_dotenv()


@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    # print("THIS IS THE stripe webhook == " , payload)
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

    if event_type == "checkout.session.completed":
        print("this is event checkout paid" , session["metadata"]["deposit_amount_cents"])
        if session["payment_status"] == "paid":
            booking_id = session["client_reference_id"]
            # booking_id = "TESTING123"
            deposit_cents = int(session["metadata"]["deposit_amount_cents"])
            # deposit_cents = 500000

            # 🔒 Idempotent DB update
            # mark_booking_paid_if_not_already(booking_id, deposit_cents)

    elif event_type == "checkout.session.expired":
        print("this is event checkout expired")
        booking_id = session.get("client_reference_id")

        # OPTIONAL: mark booking as expired/unpaid
        # mark_booking_expired(booking_id)

    return HttpResponse(status=200)


class PaymentSuccess(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        session_id = request.GET.get("session_id")

        session = stripe.checkout.Session.retrieve(session_id)

        if session.status == "expired":
            return Response({"message": "Payment link expired"}, status=400)

        if session.payment_status == "paid":
            return Response({"message": "Payment done successfully"})

        return Response({"message": "Payment not completed"}, status=400)

