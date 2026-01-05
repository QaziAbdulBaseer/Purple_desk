



# hi i want you update that (function also (send_booking_confirmation_email ))
# i want you fellow the same layout 
# first logo then then total amout and then paid amount and transction id thats it 

# keep the thing profeshion. 
# KINDLY WRITE THE COMPLEATE send_booking_confirmation_email FUNCTION ;


# utils/send_email.py

import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import os
import json
from datetime import datetime
import logging
from dotenv import load_dotenv




LOGO_URL = "http://127.0.0.1:8000/static/skyzone_logo.png"


# hi i want you update that (function also (send_booking_confirmation_email ))
# i want you fellow the same layout 
# first logo then then total amout and then paid amount and transction id thats it 

# keep the thing profeshion. 
# KINDLY WRITE THE COMPLEATE send_booking_confirmation_email FUNCTION ;
load_dotenv()
logger = logging.getLogger(__name__)

# def send_booking_confirmation_email(booking, stripe_session, deposit_amount, total_amount):
#     """
#     Send booking confirmation email to customer
#     """
#     try:
#         # Extract customer email from Stripe session
#         customer_email = stripe_session.get('customer_details', {}).get('email')
#         if not customer_email:
#             logger.error("No customer email found in Stripe session")
#             return False
        
#         # Get SendGrid API key from environment
#         sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
#         print("this is the sendgrid === " , sendgrid_api_key)
        
#         sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
        
#         # Parse booking payload for details
#         booking_details = {}
#         try:
#             payload_data = booking.payload
#             if isinstance(payload_data, str):
#                 payload_data = json.loads(payload_data)
            
#             # Extract booking details with defaults
#             booking_details = {
#                 'package_name': payload_data.get('packageDetails', {}).get('name', 'Birthday Party Package'),
#                 'package_description': payload_data.get('packageDetails', {}).get('description', ''),
#                 'booking_date': payload_data.get('bookingDate', ''),
#                 'booking_time': booking.booking_time or 'Not specified',
#                 'guest_of_honor': payload_data.get('comments', '').replace('Guest of honor: ', ''),
#                 'location_name': booking.location_id.location_name if booking.location_id else 'Sky Zone',
#                 'total_amount': total_amount,
#                 'deposit_paid': deposit_amount,
#                 'booking_id': booking.external_id or booking.booking_unique_id,
#                 'customer_name': f"{booking.customer.first_name} {booking.customer.last_name}" if booking.customer else 'Customer',
#                 'customer_email': customer_email,
#                 'customer_phone': booking.customer.phone_number if booking.customer else '',
#                 'stripe_payment_id': stripe_session.get('payment_intent', '')
#             }
#         except Exception as e:
#             logger.error(f"Error parsing booking details for email: {str(e)}", exc_info=True)
#             # Use basic details
#             booking_details = {
#                 'package_name': 'Birthday Party Package',
#                 'booking_date': booking.booking_date or '',
#                 'booking_time': booking.booking_time or 'Not specified',
#                 'location_name': booking.location_id.location_name if booking.location_id else 'Sky Zone',
#                 'total_amount': total_amount,
#                 'deposit_paid': deposit_amount,
#                 'booking_id': booking.external_id or booking.booking_unique_id or 'Unknown',
#                 'customer_name': f"{booking.customer.first_name} {booking.customer.last_name}" if booking.customer else 'Customer',
#                 'customer_email': customer_email,
#                 'customer_phone': booking.customer.phone_number if booking.customer else '',
#                 'stripe_payment_id': stripe_session.get('payment_intent', 'N/A')
#             }
        
#         # Email subject
#         subject = f"Booking Confirmation - {booking_details['booking_id']}"
        
#         # Email template with booking details
#         email_template = f"""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Booking Confirmation</title>
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
#             background-color: #4CAF50;
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
#             border-left: 4px solid #4CAF50;
#         }}
#         .footer {{
#             text-align: center;
#             margin-top: 20px;
#             color: #666;
#             font-size: 12px;
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
#         <h1>🎉 Booking Confirmed!</h1>
#         <p>Thank you for booking with {booking_details.get('location_name', 'Sky Zone')}</p>
#     </div>
    
#     <div class="content">
#         <h2>Hi {booking_details.get('customer_name', 'Customer')},</h2>
#         <p>Your booking has been successfully confirmed. Here are your booking details:</p>
        
        
#         <div class="details">
#             <h3>💰 Payment Details</h3>
#             <p><strong>Total Amount:</strong> ${booking_details.get('total_amount', 0)}</p>
#             <p><strong>Deposit Paid:</strong> ${booking_details.get('deposit_paid', 0)}</p>
#             <p><strong>Payment Status:</strong> ✅ Paid</p>
#             <p><strong>Transaction ID:</strong> {booking_details.get('stripe_payment_id', 'N/A')}</p>
#         </div>
        
        
#         <p>If you have any questions or need to make changes to your booking, please contact us at {booking_details.get('location_name', 'Sky Zone')} or reply to this email.</p>
        
#         <p>We look forward to making your celebration amazing!</p>
        
#         <p><strong>Best regards,</strong><br>
#         The {booking_details.get('location_name', 'Sky Zone')} Team</p>
#     </div>
    
#     <div class="footer">
#         <p>© {datetime.now().year} {booking_details.get('location_name', 'Sky Zone')}. All rights reserved.</p>
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
#             logger.info(f"Confirmation email sent successfully for booking {booking_details.get('booking_id', 'Unknown')}")
#             return True
#         else:
#             logger.error(f"Failed to send email. Status code: {response.status_code}")
#             return False
            
#     except Exception as e:
#         logger.error(f"Error sending confirmation email: {str(e)}", exc_info=True)
#         return False





# def send_booking_confirmation_email(booking, stripe_session, deposit_amount, total_amount):
#     """
#     Send booking confirmation email to customer with professional layout:
#     1. Logo at the top
#     2. Total amount
#     3. Paid amount (deposit)
#     4. Transaction ID
#     """
#     try:
#         # Extract customer email from Stripe session
#         customer_email = stripe_session.get('customer_details', {}).get('email')
#         if not customer_email:
#             logger.error("No customer email found in Stripe session")
#             return False
        
#         # Get SendGrid API key from environment
#         sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
#         logger.info(f"SendGrid API Key: {sendgrid_api_key[:10]}...")  # Log partial for security
        
#         sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
        
#         # Parse booking payload for details
#         booking_details = {}
#         try:
#             payload_data = booking.payload
#             if isinstance(payload_data, str):
#                 payload_data = json.loads(payload_data)
            
#             # Extract essential booking details
#             booking_details = {
#                 'location_name': booking.location_id.location_name if booking.location_id else 'Sky Zone',
#                 'customer_name': f"{booking.customer.first_name} {booking.customer.last_name}" if booking.customer else 'Customer',
#                 'customer_email': customer_email,
#                 'booking_id': booking.external_id or booking.booking_unique_id or f"BK-{booking.id}",
#                 'total_amount': f"${total_amount:,.2f}",
#                 'deposit_paid': f"${deposit_amount:,.2f}",
#                 'stripe_payment_id': stripe_session.get('payment_intent', ''),
#                 'stripe_transaction_id': stripe_session.get('id', ''),
#                 'booking_date': booking.booking_date.strftime("%B %d, %Y") if booking.booking_date else 'Not specified',
#                 'booking_time': booking.booking_time.strftime("%I:%M %p") if hasattr(booking.booking_time, 'strftime') else str(booking.booking_time)
#             }
#         except Exception as e:
#             logger.error(f"Error parsing booking details for email: {str(e)}", exc_info=True)
#             # Use minimal details
#             booking_details = {
#                 'location_name': 'Sky Zone',
#                 'customer_name': 'Customer',
#                 'customer_email': customer_email,
#                 'booking_id': 'Unknown',
#                 'total_amount': f"${total_amount:,.2f}",
#                 'deposit_paid': f"${deposit_amount:,.2f}",
#                 'stripe_payment_id': stripe_session.get('payment_intent', 'N/A'),
#                 'stripe_transaction_id': stripe_session.get('id', 'N/A'),
#                 'booking_date': 'Not specified',
#                 'booking_time': 'Not specified'
#             }
        
#         # Email subject
#         subject = f"Booking Confirmation #{booking_details['booking_id']}"
        
#         # Professional email template with requested layout
#         email_template = f"""<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Booking Confirmation</title>
#     <style>
#         /* Professional Styling */
#         body {{
#             font-family: 'Helvetica Neue', Arial, sans-serif;
#             line-height: 1.6;
#             color: #333333;
#             margin: 0;
#             padding: 0;
#             background-color: #f9f9f9;
#         }}
        
#         .email-container {{
#             max-width: 600px;
#             margin: 0 auto;
#             background-color: #ffffff;
#         }}
        
#         .logo-section {{
#             text-align: center;
#             padding: 30px 20px;
#             background-color: #ffffff;
#             border-bottom: 1px solid #eeeeee;
#         }}
        
#         .logo {{
#             max-width: 200px;
#             height: auto;
#         }}
        
#         .content-section {{
#             padding: 40px;
#         }}
        
#         .greeting {{
#             color: #333333;
#             margin-bottom: 30px;
#             font-size: 16px;
#             line-height: 1.5;
#         }}
        
#         .payment-details {{
#             background-color: #f8f9fa;
#             border-radius: 8px;
#             padding: 25px;
#             margin: 30px 0;
#             border-left: 4px solid #007bff;
#         }}
        
#         .payment-row {{
#             display: flex;
#             justify-content: space-between;
#             padding: 12px 0;
#             border-bottom: 1px solid #eeeeee;
#         }}
        
#         .payment-row:last-child {{
#             border-bottom: none;
#         }}
        
#         .payment-label {{
#             font-weight: 600;
#             color: #555555;
#         }}
        
#         .payment-value {{
#             font-weight: 700;
#             color: #333333;
#         }}
        
#         .total-amount {{
#             font-size: 24px;
#             color: #28a745;
#         }}
        
#         .paid-amount {{
#             font-size: 20px;
#             color: #17a2b8;
#         }}
        
#         .transaction-id {{
#             font-family: 'Courier New', monospace;
#             background-color: #f1f1f1;
#             padding: 8px 12px;
#             border-radius: 4px;
#             word-break: break-all;
#             font-size: 14px;
#             color: #495057;
#         }}
        
#         .booking-info {{
#             background-color: #f8f9fa;
#             border-radius: 8px;
#             padding: 20px;
#             margin-top: 25px;
#             font-size: 14px;
#             color: #666666;
#         }}
        
#         .footer {{
#             text-align: center;
#             padding: 30px 20px;
#             background-color: #f1f1f1;
#             color: #666666;
#             font-size: 12px;
#             border-top: 1px solid #eeeeee;
#         }}
        
#         .contact-info {{
#             margin-top: 20px;
#             font-size: 14px;
#             color: #555555;
#         }}
        
#         @media screen and (max-width: 600px) {{
#             .content-section {{
#                 padding: 20px;
#             }}
            
#             .payment-row {{
#                 flex-direction: column;
#                 align-items: flex-start;
#             }}
            
#             .payment-value {{
#                 margin-top: 5px;
#             }}
#         }}
#     </style>
# </head>
# <body>
#     <div class="email-container">
#         <!-- 1. LOGO SECTION -->
#         <div class="logo-section">
#             <img src="{LOGO_URL}" alt="Sky Zone Logo" class="logo">
#         </div>
        
#         <!-- CONTENT SECTION -->
#         <div class="content-section">
#             <div class="greeting">
#                 <p>Dear <strong>{booking_details['customer_name']}</strong>,</p>
#                 <p>Thank you for choosing {booking_details['location_name']}! Your booking has been confirmed and we're excited to host your event.</p>
#             </div>
            
#             <!-- 2. TOTAL AMOUNT -->
#             <div class="payment-details">
#                 <div class="payment-row">
#                     <span class="payment-label">Total Amount:</span>
#                     <span class="payment-value total-amount">{booking_details['total_amount']}</span>
#                 </div>
                
#                 <!-- 3. PAID AMOUNT -->
#                 <div class="payment-row">
#                     <span class="payment-label">Paid Amount (Deposit):</span>
#                     <span class="payment-value paid-amount">{booking_details['deposit_paid']}</span>
#                 </div>
                
#                 <!-- 4. TRANSACTION ID -->
#                 <div class="payment-row">
#                     <span class="payment-label">Transaction ID:</span>
#                     <div style="text-align: right;">
#                         <div class="transaction-id">{booking_details['stripe_transaction_id']}</div>
#                     </div>
#                 </div>
                
#                 <!-- Additional payment info -->
#                 <div class="payment-row">
#                     <span class="payment-label">Payment Status:</span>
#                     <span class="payment-value" style="color: #28a745;">✓ Confirmed</span>
#                 </div>
                
#                 <div class="payment-row">
#                     <span class="payment-label">Payment Method:</span>
#                     <span class="payment-value">Credit Card</span>
#                 </div>
#             </div>
            
#             <!-- Booking Information -->
#             <div class="booking-info">
#                 <p><strong>Booking Reference:</strong> {booking_details['booking_id']}</p>
#                 <p><strong>Booking Date:</strong> {booking_details['booking_date']} at {booking_details['booking_time']}</p>
#                 <p><strong>Payment Intent ID:</strong> {booking_details['stripe_payment_id']}</p>
#             </div>
            
#             <!-- Next Steps -->
#             <div style="margin-top: 30px; padding: 20px; background-color: #e8f4f8; border-radius: 8px;">
#                 <h3 style="margin-top: 0; color: #17a2b8;">Next Steps:</h3>
#                 <ol style="padding-left: 20px;">
#                     <li>Keep this email for your records</li>
#                     <li>Arrive 15 minutes before your scheduled time</li>
#                     <li>Bring valid ID for verification</li>
#                     <li>Complete remaining payment upon arrival (if applicable)</li>
#                 </ol>
#             </div>
            
#             <!-- Contact Information -->
#             <div class="contact-info">
#                 <p><strong>Need assistance?</strong></p>
#                 <p>Email: support@skyzone.com<br>
#                 Phone: (123) 456-7890<br>
#                 Hours: Monday-Friday, 9AM-6PM EST</p>
#             </div>
#         </div>
        
#         <!-- FOOTER -->
#         <div class="footer">
#             <p>© {datetime.now().year} {booking_details['location_name']}. All rights reserved.</p>
#             <p>This is an automated confirmation. Please do not reply to this email.</p>
#             <p>Sky Zone Trampoline Park | 123 Adventure Street, Fun City, FC 12345</p>
#         </div>
#     </div>
# </body>
# </html>"""
        
#         from_email = Email("bookings@skyzone.com", "Sky Zone Bookings")
        
#         # Send to customer and relevant stakeholders
#         to_emails = [
#             To(customer_email),  # Primary customer
#             To("baseer.abdul@sybrid.com"),  # Admin/Developer
#             To("bookings@skyzone.com"),  # Booking department
#         ]
        
#         content = Content("text/html", email_template)
#         mail = Mail(from_email, to_emails, subject, content)
        
#         # Get a JSON-ready representation of the Mail object
#         mail_json = mail.get()
        
#         # Send the email
#         response = sg.client.mail.send.post(request_body=mail_json)
        
#         if response.status_code in [200, 202]:
#             logger.info(f"✅ Confirmation email sent successfully for booking {booking_details['booking_id']} to {customer_email}")
#             return True
#         else:
#             logger.error(f"❌ Failed to send email. Status code: {response.status_code}")
#             logger.error(f"Response body: {response.body}")
#             return False
            
#     except Exception as e:
#         logger.error(f"❌ Error sending confirmation email: {str(e)}", exc_info=True)
#         return False




# # Keep the original function for backward compatibility
# async def send_confirmation_email():
#     """
#     Original function for backward compatibility
#     """
#     try:
#         email_template = """<!DOCTYPE html>
#                     <html lang="en">
#                     <head>
#                         <meta charset="UTF-8">
#                         <meta name="viewport" content="width=device-width, initial-scale=1.0">
#                         <title>Birthday Party Package Booking</title>
#                         <style>
#                             @media screen and (max-width: 600px) {{
#                                 .content {{
#                                     width: 100% !important;
#                                     display: block !important;
#                                     padding: 10px !important;
#                                 }}
#                                 .header, .body, .footer {{
#                                     padding: 20px !important;
#                                 }}
#                             }}
#                         </style>
#                     </head>
#                     <body style="font-family: 'Poppins', Arial, sans-serif">
#                                 <h1>This si just the testing email<h1/>
#                     </body>
#                     </html>"""
        
#         sg = sendgrid.SendGridAPIClient(api_key=os.getenv('SENDGRID_API_KEY'))
#         from_email = Email("shereen@purpledesk.ai")
        
#         to_emails = [
#             To("baseer.abdul@sybrid.com"),
#         ]
        
#         subject = "Test Email"
#         content = Content("text/html", email_template)
#         mail = Mail(from_email, to_emails, subject, content)

#         # Get a JSON-ready representation of the Mail object
#         mail_json = mail.get()

#         # Send an HTTP POST request to /mail/send
#         response = sg.client.mail.send.post(request_body=mail_json)

#         if response.status_code==200 or response.status_code==202:
#             return "Thank you. I've recorded the details of your lost item and forwarded them to our team. If the item is located, one of our Sky Zone representatives will reach out to you shortly."
#         else:
#             return f"I've noted your lost item details, but there was a technical issue while forwarding the information. I recommend reaching out to our staff directly or visiting the location for further assistance."
#     except Exception as e:
#         print(f"Failed to send email: {e}")
#         return f"I've noted your lost item details, but there was a technical issue while forwarding the information. I recommend reaching out to our staff directly or visiting the location for further assistance."



def send_booking_confirmation_email(booking, stripe_session, deposit_amount, total_amount):
    """
    Sends a professional booking confirmation email.

    Layout:
    1. Logo
    2. Total Amount
    3. Paid Amount
    4. Transaction ID
    """

    try:
        # -------------------------
        # Customer Email
        # -------------------------
        customer_email = stripe_session.get("customer_details", {}).get("email")
        if not customer_email:
            logger.error("No customer email found in Stripe session")
            return False

        # -------------------------
        # SendGrid Setup
        # -------------------------
        sendgrid_api_key = os.getenv("SENDGRID_API_KEY")
        if not sendgrid_api_key:
            logger.error("SENDGRID_API_KEY not configured")
            return False

        sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)

        # -------------------------
        # Safe Booking Values
        # -------------------------
        booking_id = (
            booking.external_id
            or booking.booking_unique_id
            or f"BOOKING-{booking.id}"
        )

        transaction_id = (
            stripe_session.get("payment_intent")
            or stripe_session.get("id")
            or "N/A"
        )

        customer_name = (
            f"{booking.customer.first_name} {booking.customer.last_name}"
            if booking.customer else "Customer"
        )

        location_name = (
            booking.location_id.location_name
            if booking.location_id else "Sky Zone"
        )

        total_amount_display = f"${float(total_amount):,.2f}"
        paid_amount_display = f"${float(deposit_amount):,.2f}"

        # -------------------------
        # Email Subject
        # -------------------------
        subject = f"Payment Confirmation – {booking_id}"

        # -------------------------
        # Email HTML (Professional & Minimal)
        # -------------------------
        email_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Booking Confirmation</title>
<style>
    body {{
        font-family: Arial, Helvetica, sans-serif;
        background-color: #f4f6f8;
        margin: 0;
        padding: 0;
        color: #333;
    }}
    .container {{
        max-width: 600px;
        margin: 30px auto;
        background: #ffffff;
        border-radius: 6px;
        overflow: hidden;
        box-shadow: 0 2px 6px rgba(0,0,0,0.05);
    }}
    .logo {{
        text-align: center;
        padding: 30px;
        border-bottom: 1px solid #eee;
    }}
    .logo img {{
        max-width: 180px;
    }}
    .content {{
        padding: 35px;
    }}
    .row {{
        display: flex;
        justify-content: space-between;
        padding: 14px 0;
        border-bottom: 1px solid #eee;
        font-size: 15px;
    }}
    .row:last-child {{
        border-bottom: none;
    }}
    .label {{
        font-weight: 600;
        color: #555;
    }}
    .value {{
        font-weight: 700;
    }}
    .total {{
        font-size: 22px;
        color: #28a745;
    }}
    .paid {{
        font-size: 18px;
        color: #007bff;
    }}
    .txn {{
        font-family: monospace;
        background: #f1f3f5;
        padding: 6px 10px;
        border-radius: 4px;
        font-size: 13px;
    }}
    .footer {{
        text-align: center;
        font-size: 12px;
        color: #777;
        background: #f1f3f5;
        padding: 20px;
    }}
</style>
</head>

<body>
    <div class="container">

        <!-- LOGO -->
        <div class="logo">
            <img src="{LOGO_URL}" alt="Sky Zone">
        </div>

        <!-- CONTENT -->
        <div class="content">
            <p>Dear <strong>{customer_name}</strong>,</p>
            <p>Your payment has been successfully processed for <strong>{location_name}</strong>.</p>

            <div class="row">
                <span class="label">Total Amount</span>
                <span class="value total">{total_amount_display}</span>
            </div>

            <div class="row">
                <span class="label">Paid Amount</span>
                <span class="value paid">{paid_amount_display}</span>
            </div>

            <div class="row">
                <span class="label">Transaction ID</span>
                <span class="txn">{transaction_id}</span>
            </div>
        </div>

        <!-- FOOTER -->
        <div class="footer">
            © {datetime.now().year} {location_name}. All rights reserved.<br>
            This is an automated email. Please do not reply.
        </div>
    </div>
</body>
</html>
"""

        # -------------------------
        # Send Email
        # -------------------------
        mail = Mail(
            from_email=Email("shereen@purpledesk.ai", "Sky Zone Bookings"),
            to_emails=[
                To(customer_email),
                To("baseer.abdul@sybrid.com"),
            ],
            subject=subject,
            html_content=Content("text/html", email_html),
        )

        response = sg.client.mail.send.post(request_body=mail.get())

        if response.status_code in (200, 202):
            logger.info(f"Confirmation email sent for booking {booking_id}")
            return True

        logger.error(f"SendGrid error: {response.status_code}")
        return False

    except Exception as e:
        logger.error("Error sending booking confirmation email", exc_info=True)
        return False



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



def build_items_from_description(description: str) -> str:
    """
    Converts packageDetails.description into HTML rows
    """
    if not description:
        return ""

    rows = ""

    # Split by |
    parts = [p.strip() for p in description.split("|")]

    for part in parts:
        # Example:
        # Epic Party Jump Package (Qty: 1, $340.00)
        rows += f"""
        <tr>
            <td style="padding:8px 0;">
                {part}
            </td>
        </tr>
        """

    return rows



LOGO_URL = "http:://127.0.0.1:8000//static/skyzone_logo.png"


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
    Sends Sky Zone styled booking email using packageDetails.description
    """

    try:
        sg = sendgrid.SendGridAPIClient(
            api_key=os.getenv("SENDGRID_API_KEY")
        )

        # Parse payload if string
        if isinstance(booking_payload, str):
            booking_payload = json.loads(booking_payload)

        # Booking meta
        booking_datetime = booking_payload.get(
            "bookingDate",
            datetime.now().strftime("%A, %B %d, %Y %I:%M %p")
        )

        location_display = location_name or "Elk Grove"

        # Package description (THIS IS THE KEY FIX)
        package_description = booking_payload.get("packageDetails", {}).get("description", "")

        order_items_html = build_items_from_description(package_description)

        # Financials
        tax_amount = float(booking_payload.get("tax", 5.77))
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

<body style="margin:0; padding:0; font-family:Arial, Helvetica, sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0">
<tr>
<td align="center">

<table width="600" cellpadding="0" cellspacing="0" style="border:1px solid #eee;">

<!-- HEADER -->
<tr>
<td style="background:#ff6a00; padding:20px; text-align:center;">
    <img src="data:image/jpeg;base64,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" width="180" alt="Sky Zone">
</td>
</tr>

<!-- MESSAGE -->
<tr>
<td style="padding:30px; text-align:center;">
    <h2 style="margin:0;">Thank you for your order!</h2>
    <p style="font-size:14px;">
        To confirm your booking,<br>
        please complete your payment using the link below.
    </p>

    <a href="{stripe_payment_link}"
       style="display:inline-block; background:#000; color:#fff;
              padding:12px 30px; text-decoration:none;
              font-weight:bold; border-radius:4px;">
        Pay Now
    </a>
</td>
</tr>

<!-- ORDER SUMMARY -->
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

        mail = Mail(
            from_email=Email("shereen@purpledesk.ai"),
            to_emails=[
                To(customer_email),
                To("baseer.abdul@sybrid.com")
            ],
            subject=subject,
            html_content=Content("text/html", email_template)
        )

        response = sg.client.mail.send.post(request_body=mail.get())

        if response.status_code in (200, 202):
            logger.info(f"Booking email sent: {booking_id}")
            return True

        logger.error(f"SendGrid failed: {response.status_code}")
        return False

    except Exception as e:
        logger.error("Email send error", exc_info=True)
        return False
