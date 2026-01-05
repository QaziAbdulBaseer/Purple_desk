





# utils/send_email.py

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
import json
from datetime import datetime
import logging
from dotenv import load_dotenv
load_dotenv()
logger = logging.getLogger(__name__)

def send_booking_confirmation_email(booking, stripe_session, deposit_amount, total_amount):
    """
    Send booking confirmation email to customer
    """
    try:
        # Extract customer email from Stripe session
        customer_email = stripe_session.get('customer_details', {}).get('email')
        if not customer_email:
            logger.error("No customer email found in Stripe session")
            return False
        
        # Get SendGrid API key from environment
        sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        print("this is the sendgrid === " , sendgrid_api_key)
        
        sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
        
        # Parse booking payload for details
        booking_details = {}
        try:
            payload_data = booking.payload
            if isinstance(payload_data, str):
                payload_data = json.loads(payload_data)
            
            # Extract booking details with defaults
            booking_details = {
                'package_name': payload_data.get('packageDetails', {}).get('name', 'Birthday Party Package'),
                'package_description': payload_data.get('packageDetails', {}).get('description', ''),
                'booking_date': payload_data.get('bookingDate', ''),
                'booking_time': booking.booking_time or 'Not specified',
                'guest_of_honor': payload_data.get('comments', '').replace('Guest of honor: ', ''),
                'location_name': booking.location_id.location_name if booking.location_id else 'Sky Zone',
                'total_amount': total_amount,
                'deposit_paid': deposit_amount,
                'booking_id': booking.external_id or booking.booking_unique_id,
                'customer_name': f"{booking.customer.first_name} {booking.customer.last_name}" if booking.customer else 'Customer',
                'customer_email': customer_email,
                'customer_phone': booking.customer.phone_number if booking.customer else '',
                'stripe_payment_id': stripe_session.get('payment_intent', '')
            }
        except Exception as e:
            logger.error(f"Error parsing booking details for email: {str(e)}", exc_info=True)
            # Use basic details
            booking_details = {
                'package_name': 'Birthday Party Package',
                'booking_date': booking.booking_date or '',
                'booking_time': booking.booking_time or 'Not specified',
                'location_name': booking.location_id.location_name if booking.location_id else 'Sky Zone',
                'total_amount': total_amount,
                'deposit_paid': deposit_amount,
                'booking_id': booking.external_id or booking.booking_unique_id or 'Unknown',
                'customer_name': f"{booking.customer.first_name} {booking.customer.last_name}" if booking.customer else 'Customer',
                'customer_email': customer_email,
                'customer_phone': booking.customer.phone_number if booking.customer else '',
                'stripe_payment_id': stripe_session.get('payment_intent', 'N/A')
            }
        
        # Email subject
        subject = f"Booking Confirmation - {booking_details['booking_id']}"
        
        # Email template with booking details
        email_template = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking Confirmation</title>
    <style>
        body {{
            font-family: 'Poppins', Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .header {{
            background-color: #4CAF50;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 5px 5px 0 0;
        }}
        .content {{
            padding: 20px;
            background-color: #f9f9f9;
            border-radius: 0 0 5px 5px;
        }}
        .details {{
            background-color: white;
            padding: 15px;
            border-radius: 5px;
            margin: 15px 0;
            border-left: 4px solid #4CAF50;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            color: #666;
            font-size: 12px;
        }}
        @media screen and (max-width: 600px) {{
            .content {{
                width: 100% !important;
                display: block !important;
                padding: 10px !important;
            }}
            .header, .body, .footer {{
                padding: 20px !important;
            }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🎉 Booking Confirmed!</h1>
        <p>Thank you for booking with {booking_details.get('location_name', 'Sky Zone')}</p>
    </div>
    
    <div class="content">
        <h2>Hi {booking_details.get('customer_name', 'Customer')},</h2>
        <p>Your booking has been successfully confirmed. Here are your booking details:</p>
        
        
        <div class="details">
            <h3>💰 Payment Details</h3>
            <p><strong>Total Amount:</strong> ${booking_details.get('total_amount', 0)}</p>
            <p><strong>Deposit Paid:</strong> ${booking_details.get('deposit_paid', 0)}</p>
            <p><strong>Payment Status:</strong> ✅ Paid</p>
            <p><strong>Transaction ID:</strong> {booking_details.get('stripe_payment_id', 'N/A')}</p>
        </div>
        
        
        <p>If you have any questions or need to make changes to your booking, please contact us at {booking_details.get('location_name', 'Sky Zone')} or reply to this email.</p>
        
        <p>We look forward to making your celebration amazing!</p>
        
        <p><strong>Best regards,</strong><br>
        The {booking_details.get('location_name', 'Sky Zone')} Team</p>
    </div>
    
    <div class="footer">
        <p>© {datetime.now().year} {booking_details.get('location_name', 'Sky Zone')}. All rights reserved.</p>
        <p>This is an automated email, please do not reply to this address.</p>
    </div>
</body>
</html>"""
        
        from_email = Email("shereen@purpledesk.ai")
        
        # Send to customer and also to admin/booking team
        to_emails = [
            To(customer_email),  # Customer
            To("baseer.abdul@sybrid.com"),  # Admin/Developer
            # Uncomment these as needed:
            # To("bookings@purpledesk.ai"),
            # To("vm@purpledesk.ai"),
            # To("elkgrove-ca@skyzone.com")
        ]
        
        content = Content("text/html", email_template)
        mail = Mail(from_email, to_emails, subject, content)
        
        # Get a JSON-ready representation of the Mail object
        mail_json = mail.get()
        
        # Send the email
        response = sg.client.mail.send.post(request_body=mail_json)
        
        if response.status_code in [200, 202]:
            logger.info(f"Confirmation email sent successfully for booking {booking_details.get('booking_id', 'Unknown')}")
            return True
        else:
            logger.error(f"Failed to send email. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"Error sending confirmation email: {str(e)}", exc_info=True)
        return False


# Keep the original function for backward compatibility
async def send_confirmation_email():
    """
    Original function for backward compatibility
    """
    try:
        email_template = """<!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8">
                        <meta name="viewport" content="width=device-width, initial-scale=1.0">
                        <title>Birthday Party Package Booking</title>
                        <style>
                            @media screen and (max-width: 600px) {{
                                .content {{
                                    width: 100% !important;
                                    display: block !important;
                                    padding: 10px !important;
                                }}
                                .header, .body, .footer {{
                                    padding: 20px !important;
                                }}
                            }}
                        </style>
                    </head>
                    <body style="font-family: 'Poppins', Arial, sans-serif">
                                <h1>This si just the testing email<h1/>
                    </body>
                    </html>"""
        
        sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
        from_email = Email("shereen@purpledesk.ai")
        
        to_emails = [
            To("baseer.abdul@sybrid.com"),
        ]
        
        subject = "Test Email"
        content = Content("text/html", email_template)
        mail = Mail(from_email, to_emails, subject, content)

        # Get a JSON-ready representation of the Mail object
        mail_json = mail.get()

        # Send an HTTP POST request to /mail/send
        response = sg.client.mail.send.post(request_body=mail_json)

        if response.status_code==200 or response.status_code==202:
            return "Thank you. I've recorded the details of your lost item and forwarded them to our team. If the item is located, one of our Sky Zone representatives will reach out to you shortly."
        else:
            return f"I've noted your lost item details, but there was a technical issue while forwarding the information. I recommend reaching out to our staff directly or visiting the location for further assistance."
    except Exception as e:
        print(f"Failed to send email: {e}")
        return f"I've noted your lost item details, but there was a technical issue while forwarding the information. I recommend reaching out to our staff directly or visiting the location for further assistance."


# utils/send_email.py - Add this new function

# def send_booking_details_email(customer_name, customer_email, booking_id, stripe_payment_link, total_amount, booking_payload, location_name=None):
#     """
#     Send booking details email with Stripe payment link to customer
#     This email is sent when the booking is created but payment is pending
    
#     Args:
#         customer_name: Customer's full name
#         customer_email: Customer's email address
#         booking_id: Booking ID
#         stripe_payment_link: Stripe payment URL
#         total_amount: Total booking amount in dollars
#         booking_payload: Complete booking payload (dict or JSON string)
#         location_name: Name of the location (optional)
#     """
#     try:
#         # Get SendGrid API key from environment
#         sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        
#         sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
        
#         # Parse booking payload if it's a string
#         if isinstance(booking_payload, str):
#             try:
#                 booking_payload = json.loads(booking_payload)
#             except:
#                 booking_payload = {"raw": booking_payload}
        
#         # Extract booking details
#         booking_date = booking_payload.get('bookingDate', 'Not specified')
#         booking_time = None
        
#         # Extract booking time from items or products
#         if 'items' in booking_payload and booking_payload['items']:
#             booking_time = booking_payload['items'][0].get('startTime', 'Not specified')
#         elif 'products' in booking_payload and booking_payload['products']:
#             booking_time = booking_payload['products'][0].get('startTime', 'Not specified')
        
#         # # Extract package details
#         # package_name = booking_payload.get('packageDetails', {}).get('name', 'Birthday Party Package')
#         # package_description = booking_payload.get('packageDetails', {}).get('description', '')
#         package_name = booking_payload.get('packageDetails', {}).get('name', 'Birthday Party Package')
#         package_description = booking_payload.get('packageDetails', {}).get('description', '')

        
#         # Extract items/products count
#         items_count = len(booking_payload.get('items', [])) if booking_payload.get('items') else 0
#         products_count = len(booking_payload.get('products', [])) if booking_payload.get('products') else 0
        
#         # Calculate deposit amount if available
#         deposit_percentage = booking_payload.get('depositPercentage', 0)
#         deposit_amount = (total_amount * deposit_percentage) / 100 if deposit_percentage > 0 else 0
        
#         # Email subject
#         subject = f"Booking Details - {booking_id}"
        
#         # Email template with booking details
#         email_template = f"""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Booking Details</title>
#     <style>
#         body {{
#             font-family: 'Poppins', Arial, sans-serif;
#             line-height: 1.6;
#             color: #333;
#             max-width: 600px;
#             margin: 0 auto;
#             padding: 20px;
#         }}
#         .header {{
#             background-color: #0074d4;
#             color: white;
#             padding: 20px;
#             text-align: center;
#             border-radius: 5px 5px 0 0;
#         }}
#         .content {{
#             padding: 20px;
#             background-color: #f9f9f9;
#             border-radius: 0 0 5px 5px;
#         }}
#         .details {{
#             background-color: white;
#             padding: 15px;
#             border-radius: 5px;
#             margin: 15px 0;
#             border-left: 4px solid #0074d4;
#         }}
#         .payment-link {{
#             text-align: center;
#             margin: 25px 0;
#             padding: 20px;
#             background-color: #e6f7ff;
#             border-radius: 5px;
#             border: 2px dashed #0074d4;
#         }}
#         .payment-button {{
#             display: inline-block;
#             background-color: #0074d4;
#             color: white;
#             padding: 12px 30px;
#             text-decoration: none;
#             border-radius: 5px;
#             font-weight: bold;
#             font-size: 16px;
#             margin: 10px 0;
#         }}
#         .footer {{
#             text-align: center;
#             margin-top: 20px;
#             color: #666;
#             font-size: 12px;
#         }}
#         .booking-items {{
#             background-color: #f5f5f5;
#             padding: 10px;
#             border-radius: 3px;
#             margin: 10px 0;
#             font-size: 14px;
#         }}
#         @media screen and (max-width: 600px) {{
#             .content {{
#                 width: 100% !important;
#                 display: block !important;
#                 padding: 10px !important;
#             }}
#             .header, .body, .footer {{
#                 padding: 20px !important;
#             }}
#         }}
#     </style>
# </head>
# <body>
#     <div class="header">
#         <h1>📅 Your Booking Details</h1>
#         <p>Complete your payment to confirm your booking</p>
#     </div>
    
#     <div class="content">
#         <h2>Hi {customer_name},</h2>
#         <p>Thank you for choosing {location_name or 'Sky Zone'}! Your booking has been created and is ready for payment.</p>
        
        
#         <div class="details">
#             <h3>💰 Payment Information</h3>
#             <p><strong>Total Amount:</strong> ${total_amount:.2f}</p>
#             <p><strong>Deposit Required:</strong> ${deposit_amount:.2f} ({deposit_percentage}%)</p>
#             <p><strong>Payment Status:</strong> ⏳ Pending</p>
#             <p><strong>Payment Due:</strong> Please complete payment within 24 hours to secure your booking</p>
#         </div>
        
        
#         <div class="details">
#             <h3>📝 Booking Package</h3>

#             <div class="booking-items">
#                 <p><strong>Package Name:</strong></p>
#                 <p>{ package_name}</p>

#                 <p style="margin-top: 10px;"><strong>Description:</strong></p>
#                 <p>{ package_description }</p>

#                 <a href="{stripe_payment_link}" class="payment-button">Pay Now ${deposit_amount:.2f}</a>

#             </div>
#         </div>

        
        
#         <p><strong>Need Help?</strong><br>
#         If you have any questions or need to make changes to your booking, please contact us at {location_name or 'Sky Zone'} or reply to this email.</p>
        
#         <p><strong>Note:</strong> Your booking will be automatically cancelled if payment is not completed within 24 hours.</p>
        
#         <p><strong>Best regards,</strong><br>
#         The {location_name or 'Sky Zone'} Team</p> 
#     </div>
    
#     <div class="footer">
#         <p>© {datetime.now().year} {location_name or 'Sky Zone'}. All rights reserved.</p>
#         <p>This is an automated email, please do not reply to this address.</p>
#     </div>
# </body>
# </html>"""
        
#         from_email = Email("shereen@purpledesk.ai")
        
#         # Send to customer and also to admin/booking team
#         to_emails = [
#             To(customer_email),  # Customer
#             To("baseer.abdul@sybrid.com"),  # Admin/Developer
#             # Uncomment these as needed:
#             # To("bookings@purpledesk.ai"),
#             # To("vm@purpledesk.ai"),
#             # To("elkgrove-ca@skyzone.com")
#         ]
        
#         content = Content("text/html", email_template)
#         mail = Mail(from_email, to_emails, subject, content)
        
#         # Get a JSON-ready representation of the Mail object
#         mail_json = mail.get()
        
#         # Send the email
#         response = sg.client.mail.send.post(request_body=mail_json)
        
#         if response.status_code in [200, 202]:
#             logger.info(f"Booking details email sent successfully for booking {booking_id}")
#             return True
#         else:
#             logger.error(f"Failed to send booking details email. Status code: {response.status_code}")
#             return False
            
#     except Exception as e:
#         logger.error(f"Error sending booking details email: {str(e)}", exc_info=True)
#         return False






import os
import json
import sendgrid
from datetime import datetime
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging

logger = logging.getLogger(__name__)

LOGO_URL = "http://127.0.0.1:8000/static/skyzone_logo.png"


def build_order_items_html(items):
    """
    Builds dynamic HTML rows for order items
    """
    rows = ""

    for item in items:
        name = item.get("name", "Item")
        qty = item.get("quantity", 1)
        price = float(item.get("price", 0))

        rows += f"""
        <tr>
            <td style="padding:8px 0;">
                <strong>{name}</strong><br>
                <span style="color:#666;">Qty: {qty}</span>
            </td>
            <td style="padding:8px 0; text-align:right;">
                ${price:.2f}
            </td>
        </tr>
        """

    return rows


def send_booking_details_email(
    customer_name,
    customer_email,
    booking_id,
    stripe_payment_link,
    total_amount,
    booking_payload,
    location_name=None
):
    """
    Sends Sky Zone styled booking payment email with Stripe Pay Now link
    """

    try:
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)

        # Parse payload if string
        if isinstance(booking_payload, str):
            booking_payload = json.loads(booking_payload)

        # Booking meta
        booking_datetime = booking_payload.get(
            "bookingDateTime",
            datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        )

        location_display = location_name or "Sky Zone"

        # Items
        items = booking_payload.get("items") or booking_payload.get("products") or []
        order_items_html = build_order_items_html(items)

        # Financials
        tax_amount = float(booking_payload.get("tax", 0))
        deposit_percentage = float(booking_payload.get("depositPercentage", 0))
        min_deposit = (total_amount * deposit_percentage) / 100 if deposit_percentage else 0

        subject = "Thank you for your order!"

        email_template = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Sky Zone Order</title>
</head>

<body style="margin:0; padding:0; font-family:Arial, Helvetica, sans-serif; background:#ffffff;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0" style="border:1px solid #eee;">

<tr>
<td style="background:#ff6a00; padding:20px; text-align:center;">
    <img src="{LOGO_URL}" alt="Sky Zone" width="180" style="display:block; margin:auto;">
</td>
</tr>

<tr>
<td style="padding:30px; text-align:center;">
    <h2 style="margin:0;">Thank you for your order!</h2>
    <p style="margin:10px 0; font-size:14px;">
        To confirm your booking,<br>
        please complete your payment using the link below.
    </p>

    <a href="{stripe_payment_link}"
       style="display:inline-block; background:#000; color:#fff;
              padding:12px 30px; text-decoration:none;
              font-weight:bold; border-radius:4px; margin-top:15px;">
        Pay Now
    </a>
</td>
</tr>

<tr>
<td style="padding:20px;">
    <h3 style="border-bottom:1px solid #ddd; padding-bottom:8px;">
        Order Summary
    </h3>

    <p style="font-size:14px;">
        <strong>Transaction ID:</strong> {booking_id}<br>
        {booking_datetime}<br>
        {location_display}
    </p>

    <table width="100%" cellpadding="0" cellspacing="0">
        {order_items_html}
    </table>

    <hr style="margin:20px 0;">

    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td>Tax</td>
            <td align="right">${tax_amount:.2f}</td>
        </tr>
        <tr>
            <td style="padding-top:10px;"><strong>Grand Total</strong></td>
            <td align="right" style="padding-top:10px;">
                <strong>${total_amount:.2f}</strong>
            </td>
        </tr>
        <tr>
            <td style="padding-top:10px;"><strong>Min. Deposit</strong></td>
            <td align="right" style="padding-top:10px;">
                <strong>${min_deposit:.2f}</strong>
            </td>
        </tr>
    </table>
</td>
</tr>

</table>

</td>
</tr>
</table>
</body>
</html>
"""

        from_email = Email("shereen@purpledesk.ai")

        to_emails = [
            To(customer_email),
            To("baseer.abdul@sybrid.com")
        ]

        content = Content("text/html", email_template)
        mail = Mail(from_email, to_emails, subject, content)

        response = sg.client.mail.send.post(request_body=mail.get())

        if response.status_code in (200, 202):
            logger.info(f"Booking email sent for {booking_id}")
            return True

        logger.error(f"SendGrid error: {response.status_code}")
        return False

    except Exception as e:
        logger.error(f"Email send failed: {str(e)}", exc_info=True)
        return False
