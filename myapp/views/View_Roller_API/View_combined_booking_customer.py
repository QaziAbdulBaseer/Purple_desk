# hi I have to modified that model and flow. 
# first i need few new coloums in my booking table 
# # 1) boooking status   (by default its (live) ,)
# 2) I need one mroe colum is location id. its  a FKey from the location table.
# 3) and the locatoin id will come in the payload with name of client_id
# 4) and 3 coloum is_booking_paid this is default false
# 5) i have to update the name of coloum (doposit_made) to keep its name = (doposit_made_in_doller)

# And i also want to update the flow. 

# I want when the api hit. The first task is to keep the booking on (roller_api)
# if the roller_api is success full then move forword and add the customer in database and booking data in database and generate the stript link

# but if because of any reason the roller_booking_api failed and booking is not created on the roller_api
# then stop and just return the failed resoponse that booking is not create because to that reason.abs
# so in simple word first you have to create a roller_booking if is success then store data in customer and booking tables and then generate the stripe link
# if by any case the roller booking is not created then you donto have do anyother thing 

# like if the resposne ==     "roller_booking": {
        # "success": true,
        # "response": {
        #     "errors": [
        #         {
        #             "name": "SingleBookingLocationCapacity",
        #             "message": "No available single booking location(s) at this time - 20260103 @ 1015"
        #         }
        #     ]
        # },

# Then donot save the data in the database and generate the stripe link

# I wil give you all the retative code. you have to tell in in which file i have to past which code 





#

# myapp/views/View_Roller_API/View_combined_booking_customer.py

import json
import asyncio
import aiohttp
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction
from datetime import datetime, timedelta
import uuid
import requests
from django.utils import timezone

from myapp.model.customer_details_model import CustomerDetails
from myapp.model.roller_booking_model import RollerBookingDetails
from myapp.model.locations_model import Location
from myapp.serializers import CustomerDetailsSerializer, RollerBookingDetailsSerializer
from myapp.utils.roller_token_manager import get_or_refresh_roller_token
import logging
from myapp.utils.stripe_utils_test import create_deposit_payment_link

logger = logging.getLogger(__name__)

class CombinedBookingCustomerAPI(APIView):
    """
    Combined API to handle customer and booking creation in one request
    Accepts complete payload and automatically creates/updates customer and booking
    Also creates booking in Roller system
    """
    permission_classes = [AllowAny]
    
    # def post(self, request):
    #     """
    #     Create/Update customer and booking in one API call
    #     Also creates booking in Roller system
        
    #     Request Body (example):
    #     {
    #         "products": [...],
    #         "customer": {
    #             "Email": "test@example.com",
    #             "Phone": "1234567890",
    #             "first_name": "John",
    #             "LastName": "Doe"
    #         },
    #         "client_id": 1,
    #         "bookingDate": "2024-01-15",
    #         "comments": "Guest of honor: James",
    #         "fullPay": false,
    #         "depositPercentage": 50.0,
    #         "depositAmount": null
    #     }
    #     """
    #     try:
    #         # Step 1: Validate request
    #         complete_payload = request.data
    #         logger.info(f"Complete payload received for combined booking")
            
    #         customer_detail = complete_payload.get('customer', {})
            
    #         if not customer_detail:
    #             return Response({
    #                 'success': False,
    #                 'message': 'customer is required in payload'
    #             }, status=status.HTTP_400_BAD_REQUEST)
            
    #         # Map the incoming fields to your model fields
    #         customer_email = customer_detail.get('Email')
    #         if not customer_email:
    #             return Response({
    #                 'success': False,
    #                 'message': 'Email is required in customer'
    #             }, status=status.HTTP_400_BAD_REQUEST)
            
    #         # Step 2: Prepare customer data (but don't save yet)
    #         customer_data_for_serializer = {
    #             'customer_email': customer_email,
    #             'phone_number': customer_detail.get('Phone', ''),
    #             'first_name': customer_detail.get('first_name', ''),
    #             'last_name': customer_detail.get('LastName', '')
    #         }
            
    #         # Step 3: Get Roller API token
    #         client_id = complete_payload.get('client_id')
    #         if not client_id:
    #             return Response({
    #                 'success': False,
    #                 'message': 'client_id is required for Roller booking'
    #             }, status=status.HTTP_400_BAD_REQUEST)
            
    #         try:
    #             logger.info(f"Fetching location for client_id: {client_id}")
    #             location = Location.objects.get(location_id=client_id)
    #             logger.info(f"Location found: {location.location_name} (ID: {location.location_id})")
    #         except Location.DoesNotExist:
    #             logger.error(f"Location with ID {client_id} not found")
    #             return Response({
    #                 'success': False,
    #                 'message': f'Location with ID {client_id} not found'
    #             }, status=status.HTTP_404_NOT_FOUND)
            
    #         # Get Roller token with retry logic
    #         roller_token = None
    #         retry_count = 0
    #         max_retries = 2
            
    #         while not roller_token and retry_count < max_retries:
    #             roller_token = get_or_refresh_roller_token(location)
    #             if not roller_token:
    #                 logger.warning(f"Attempt {retry_count + 1} failed to get Roller token for location {location.location_name}")
    #                 retry_count += 1
    #                 # Force token refresh by invalidating current token
    #                 if retry_count < max_retries:
    #                     location.roller_access_token = None
    #                     location.save(update_fields=['roller_access_token'])
            
    #         if not roller_token:
    #             logger.error(f"Failed to get Roller API token for location {location.location_name} after {max_retries} attempts")
    #             return Response({
    #                 'success': False,
    #                 'message': 'Failed to get Roller API token'
    #             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    #         logger.info(f"Successfully obtained Roller token for location {location.location_name}")
            
    #         # Generate a unique booking ID (we'll use this later if Roller booking is successful)
    #         booking_unique_id = f"BK{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8].upper()}"
            
    #         # Step 4: Create booking in Roller system FIRST
    #         roller_booking_response = self._create_roller_booking_with_retry(
    #             complete_payload, roller_token, location
    #         )
            
    #         # Check if Roller booking was successful
    #         roller_success = roller_booking_response is not None and 'error' not in roller_booking_response
            
    #         if not roller_success:
    #             logger.error(f"Roller booking failed: {roller_booking_response}")
    #             return Response({
    #                 'success': False,
    #                 'message': 'Failed to create booking in Roller system',
    #                 'roller_error': roller_booking_response
    #             }, status=status.HTTP_424_FAILED_DEPENDENCY)  # 424 Failed Dependency
            
    #         # Step 5: If Roller booking successful, create local booking and customer
    #         logger.info(f"Roller booking successful, proceeding with local storage")
            
    #         with transaction.atomic():
    #             # Check if customer already exists - using customer_email field
    #             existing_customer = CustomerDetails.objects.filter(
    #                 customer_email=customer_email
    #             ).first()
                
    #             # Create or update customer
    #             if existing_customer:
    #                 # Update existing customer
    #                 customer_serializer = CustomerDetailsSerializer(
    #                     existing_customer, 
    #                     data=customer_data_for_serializer, 
    #                     partial=True
    #                 )
    #                 if customer_serializer.is_valid():
    #                     customer = customer_serializer.save()
    #                     customer_message = "Customer updated successfully"
    #                     logger.info(f"Customer updated: {customer_email}")
    #                 else:
    #                     return Response({
    #                         'success': False,
    #                         'message': 'Error updating existing customer',
    #                         'errors': customer_serializer.errors
    #                     }, status=status.HTTP_400_BAD_REQUEST)
    #             else:
    #                 # Create new customer
    #                 customer_serializer = CustomerDetailsSerializer(data=customer_data_for_serializer)
    #                 if customer_serializer.is_valid():
    #                     customer = customer_serializer.save()
    #                     customer_message = "Customer created successfully"
    #                     logger.info(f"Customer created: {customer_email}")
    #                 else:
    #                     return Response({
    #                         'success': False,
    #                         'message': 'Error creating new customer',
    #                         'errors': customer_serializer.errors
    #                     }, status=status.HTTP_400_BAD_REQUEST)
                
    #             # Step 6: Create local booking
    #             booking_data = {
    #                 'customer': customer.customer_id,
    #                 'roller_id': str(client_id),
    #                 'booking_unique_id': booking_unique_id,
    #                 'booking_date': complete_payload.get('bookingDate', ''),
    #                 'booking_time': self._extract_booking_time(complete_payload),
    #                 'capacity_reservation_id': self._generate_capacity_id(),
    #                 'payment_made': complete_payload.get('fullPay', False),
    #                 'payload': json.dumps(complete_payload)  # Store entire payload as JSON string
    #             }
                
    #             # Add Roller response to payload before saving
    #             current_payload = json.loads(complete_payload) if isinstance(complete_payload, str) else complete_payload
    #             current_payload['roller_response'] = roller_booking_response
    #             booking_data['payload'] = json.dumps(current_payload)
    #             print("this is the payload === " ,  current_payload)
    #             print("This is hte = packageDetails" , current_payload["packageDetails"])
    #             print("This is The package Name" , current_payload["packageDetails"]["name"])
    #             total_amount_dollars = current_payload["total_amount_dollars"]
    #             booking_id = current_payload["externalId"]
    #             deposit_percentage = current_payload["depositPercentage"]
    #             minimum_deposit_amount_dollars = current_payload["minimum_deposit_amount_dollars"]
    #             product_data = current_payload["packageDetails"]

    #             payment_url = create_deposit_payment_link(total_amount_dollars  ,booking_id , deposit_percentage, minimum_deposit_amount_dollars, product_data )
    #             print("This is the payment Url == " , payment_url)
    #             # return payment_url
    #             # Create booking in our database
    #             booking_serializer = RollerBookingDetailsSerializer(data=booking_data)
                
    #             if booking_serializer.is_valid():
    #                 booking = booking_serializer.save()
    #                 logger.info(f"Booking created in local database: {booking_unique_id}")
                    
    #                 # Step 7: Prepare response
    #                 response_data = {
    #                     'success': True,
    #                     'message': 'Customer and booking processed successfully',
    #                     'customer': {
    #                         'action': 'updated' if existing_customer else 'created',
    #                         'message': customer_message,
    #                         'customer_id': customer.customer_id,
    #                         'email': customer.customer_email,
    #                         'phone': customer.phone_number,
    #                         'name': f"{customer.first_name} {customer.last_name}"
    #                     },
    #                     'booking': {
    #                         'booking_id': booking.booking_id,
    #                         'booking_unique_id': booking.booking_unique_id,
    #                         'booking_date': booking.booking_date,
    #                         'payment_made': booking.payment_made,
    #                         'creation_date': booking.creation_date.strftime('%Y-%m-%d %H:%M:%S') if booking.creation_date else None
    #                     },
    #                     'roller_booking': {
    #                         'success': True,
    #                         'response': roller_booking_response,
    #                         'roller_booking_id': roller_booking_response.get('id'),
    #                         'roller_external_id': roller_booking_response.get('externalId')
    #                     },
    #                     'payload_summary': {
    #                         'total_products': len(complete_payload.get('products', [])),
    #                         'total_items': len(complete_payload.get('items', [])),
    #                         'booking_date': complete_payload.get('bookingDate'),
    #                         'comments': complete_payload.get('comments'),
    #                         'client_id': client_id
    #                     },
    #                     'stripe':{
    #                         "payment_url" :payment_url
    #                     },
    #                 }
                    
    #                 return Response(response_data, status=status.HTTP_201_CREATED)
                
    #             logger.error(f"Error creating local booking after Roller success: {booking_serializer.errors}")
    #             return Response({
    #                 'success': False,
    #                 'message': 'Roller booking successful but failed to create local booking',
    #                 'errors': booking_serializer.errors,
    #                 'roller_booking_id': roller_booking_response.get('id')
    #             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
    #     except Exception as e:
    #         logger.error(f"Error processing combined booking request: {str(e)}", exc_info=True)
    #         return Response({
    #             'success': False,
    #             'message': 'Error processing combined booking request',
    #             'error': str(e)
    #         }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def post(self, request):
        """
        Create/Update customer and booking in one API call
        First creates booking in Roller system, then saves locally if successful
        """
        try:
            # Step 1: Validate request
            complete_payload = request.data
            logger.info(f"Complete payload received for combined booking")
            
            customer_detail = complete_payload.get('customer', {})
            
            if not customer_detail:
                return Response({
                    'success': False,
                    'message': 'customer is required in payload'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Map the incoming fields to your model fields
            customer_email = customer_detail.get('Email')
            if not customer_email:
                return Response({
                    'success': False,
                    'message': 'Email is required in customer'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Step 2: Get location from client_id
            client_id = complete_payload.get('client_id')
            if not client_id:
                return Response({
                    'success': False,
                    'message': 'client_id is required for Roller booking'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                logger.info(f"Fetching location for client_id: {client_id}")
                location = Location.objects.get(location_id=client_id)
                logger.info(f"Location found: {location.location_name} (ID: {location.location_id})")
            except Location.DoesNotExist:
                logger.error(f"Location with ID {client_id} not found")
                return Response({
                    'success': False,
                    'message': f'Location with ID {client_id} not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Step 3: Get Roller API token
            roller_token = None
            retry_count = 0
            max_retries = 2
            
            while not roller_token and retry_count < max_retries:
                roller_token = get_or_refresh_roller_token(location)
                if not roller_token:
                    logger.warning(f"Attempt {retry_count + 1} failed to get Roller token for location {location.location_name}")
                    retry_count += 1
                    # Force token refresh by invalidating current token
                    if retry_count < max_retries:
                        location.roller_access_token = None
                        location.save(update_fields=['roller_access_token'])
            
            if not roller_token:
                logger.error(f"Failed to get Roller API token for location {location.location_name} after {max_retries} attempts")
                return Response({
                    'success': False,
                    'message': 'Failed to get Roller API token'
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            logger.info(f"Successfully obtained Roller token for location {location.location_name}")
            print("This is the compleate _payload = " , complete_payload)
            # Step 4: Create booking in Roller system FIRST
            roller_booking_response = self._create_roller_booking_with_retry(
                complete_payload, roller_token, location
            )
            print("this is the boooking  response = " , roller_booking_response)
            
            # Step 5: Check if Roller booking was successful
            if not self._is_roller_booking_successful(roller_booking_response):
                logger.error(f"Roller booking failed: {roller_booking_response}")
                return Response({
                    'success': False,
                    'message': 'Failed to create booking in Roller system',
                    'roller_error': roller_booking_response
                }, status=status.HTTP_424_FAILED_DEPENDENCY)
            
            # Step 6: Only if Roller booking is successful, proceed with local storage
            logger.info(f"Roller booking successful, proceeding with local storage")
            
            # Prepare customer data
            customer_data_for_serializer = {
                'customer_email': customer_email,
                'phone_number': customer_detail.get('Phone', ''),
                'first_name': customer_detail.get('first_name', ''),
                'last_name': customer_detail.get('LastName', '')
            }
            
            with transaction.atomic():
                # Check if customer already exists
                existing_customer = CustomerDetails.objects.filter(
                    customer_email=customer_email
                ).first()
                
                # Create or update customer
                if existing_customer:
                    customer_serializer = CustomerDetailsSerializer(
                        existing_customer, 
                        data=customer_data_for_serializer, 
                        partial=True
                    )
                    if customer_serializer.is_valid():
                        customer = customer_serializer.save()
                        customer_message = "Customer updated successfully"
                        logger.info(f"Customer updated: {customer_email}")
                    else:
                        return Response({
                            'success': False,
                            'message': 'Error updating existing customer',
                            'errors': customer_serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                else:
                    customer_serializer = CustomerDetailsSerializer(data=customer_data_for_serializer)
                    if customer_serializer.is_valid():
                        customer = customer_serializer.save()
                        customer_message = "Customer created successfully"
                        logger.info(f"Customer created: {customer_email}")
                    else:
                        return Response({
                            'success': False,
                            'message': 'Error creating new customer',
                            'errors': customer_serializer.errors
                        }, status=status.HTTP_400_BAD_REQUEST)
                
                # Generate a unique booking ID
                booking_unique_id = f"BK{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8].upper()}"
                
                # Step 7: Create local booking with new fields
                booking_data = {
                    'customer': customer.customer_id,
                    'location_id': location.location_id,  # New field from client_id
                    'roller_id': str(client_id),
                    'booking_unique_id': booking_unique_id,
                    'booking_date': complete_payload.get('bookingDate', ''),
                    'booking_time': self._extract_booking_time(complete_payload),
                    'payment_made': complete_payload.get('fullPay', False),
                    'booking_status': 'live',  # Default value
                    'is_booking_paid': False,  # Default value
                    'deposit_made_in_doller': complete_payload.get('depositAmount', None),  # Renamed field
                    'payload': json.dumps(complete_payload)
                }
                
                # Add Roller response to payload before saving
                current_payload = json.loads(complete_payload) if isinstance(complete_payload, str) else complete_payload
                current_payload['roller_response'] = roller_booking_response
                booking_data['payload'] = json.dumps(current_payload)
                
                # Extract data for Stripe
                total_amount_dollars = current_payload.get("total_amount_dollars", 0)
                booking_id = current_payload.get("externalId", booking_unique_id)
                deposit_percentage = current_payload.get("depositPercentage", 0)
                minimum_deposit_amount_dollars = current_payload.get("minimum_deposit_amount_dollars", 0)
                product_data = current_payload.get("packageDetails", {})
                
                # Create booking in our database
                booking_serializer = RollerBookingDetailsSerializer(data=booking_data)
                
                if booking_serializer.is_valid():
                    booking = booking_serializer.save()
                    logger.info(f"Booking created in local database: {booking_unique_id}")
                    
                    # Step 8: Generate Stripe payment link
                    payment_url = create_deposit_payment_link(
                        total_amount_dollars,
                        booking_id,
                        deposit_percentage,
                        minimum_deposit_amount_dollars,
                        product_data
                    )
                    logger.info(f"Stripe payment URL generated: {payment_url}")
                    
                    # Step 9: Prepare response
                    response_data = {
                        'success': True,
                        'message': 'Customer and booking processed successfully',
                        'customer': {
                            'action': 'updated' if existing_customer else 'created',
                            'message': customer_message,
                            'customer_id': customer.customer_id,
                            'email': customer.customer_email,
                            'phone': customer.phone_number,
                            'name': f"{customer.first_name} {customer.last_name}"
                        },
                        'booking': {
                            'booking_id': booking.booking_id,
                            'booking_unique_id': booking.booking_unique_id,
                            'booking_date': booking.booking_date,
                            'booking_status': booking.booking_status,
                            'is_booking_paid': booking.is_booking_paid,
                            'location_id': booking.location_id.location_id if booking.location_id else None,
                            'payment_made': booking.payment_made,
                            'creation_date': booking.creation_date.strftime('%Y-%m-%d %H:%M:%S') if booking.creation_date else None
                        },
                        'roller_booking': {
                            'success': True,
                            'response': roller_booking_response,
                            'roller_booking_id': roller_booking_response.get('id'),
                            'roller_external_id': roller_booking_response.get('externalId')
                        },
                        'stripe': {
                            "payment_url": payment_url
                        },
                    }
                    
                    return Response(response_data, status=status.HTTP_201_CREATED)
                
                logger.error(f"Error creating local booking after Roller success: {booking_serializer.errors}")
                return Response({
                    'success': False,
                    'message': 'Roller booking successful but failed to create local booking',
                    'errors': booking_serializer.errors,
                    'roller_booking_id': roller_booking_response.get('id')
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
                
        except Exception as e:
            logger.error(f"Error processing combined booking request: {str(e)}", exc_info=True)
            return Response({
                'success': False,
                'message': 'Error processing combined booking request',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # def _is_roller_booking_successful(self, roller_booking_response):
    #     """
    #     Check if Roller booking was successful based on response structure
    #     """
    #     if not roller_booking_response or not isinstance(roller_booking_response, dict):
    #         return False
        
    #     # Check for token or network errors
    #     if 'error' in roller_booking_response:
    #         return False
        
    #     # Check for errors array in response (as per your example)
    #     if roller_booking_response.get('success') is True:
    #         # Check if response has errors array with content
    #         response_data = roller_booking_response.get('response', {})
    #         if isinstance(response_data, dict):
    #             errors = response_data.get('errors', [])
    #             if errors and len(errors) > 0:
    #                 logger.error(f"Roller booking has errors: {errors}")
    #                 return False
    #         return True
        
    #     # Alternative: Check if we have a booking ID
    #     if 'id' in roller_booking_response:
    #         return True
        
    #     return False


    def _is_roller_booking_successful(self, roller_booking_response):
        """
        Check if Roller booking was successful based on response structure
        """
        if not roller_booking_response or not isinstance(roller_booking_response, dict):
            return False

        # Explicit error indicator
        if 'error' in roller_booking_response:
            return False

        # Case 1: Actual Roller success response (current)
        if (
            roller_booking_response.get('bookingReference')
            and roller_booking_response.get('uniqueId')
        ):
            return True

        # Case 2: Wrapped success response
        if roller_booking_response.get('success') is True:
            response_data = roller_booking_response.get('response', {})
            if isinstance(response_data, dict):
                errors = response_data.get('errors', [])
                if errors:
                    logger.error(f"Roller booking has errors: {errors}")
                    return False
            return True

        # Case 3: Legacy / alternate response
        if 'id' in roller_booking_response:
            return True

        return False


    def _create_roller_booking_with_retry(self, payload, api_token, location):
        """
        Create booking in Roller system with retry logic for token expiration
        
        Args:
            payload: Booking payload
            api_token: Initial API token
            location: Location object
        
        Returns:
            Dict with Roller API response or error dict
        """
        max_retries = 2
        retry_count = 0
        print("this is test 1")
        while retry_count < max_retries:
            try:
                roller_response = self._create_roller_booking_sync(payload, api_token)
                
                # Check if token is expired
                if self._is_token_expired_error(roller_response):
                    logger.warning(f"Token expired error detected for location {location.location_name}, refreshing token...")
                    
                    # Force refresh token
                    location.roller_access_token = None
                    location.save(update_fields=['roller_access_token'])
                    
                    # Get new token
                    new_token = get_or_refresh_roller_token(location)
                    if not new_token:
                        logger.error(f"Failed to refresh token for location {location.location_name}")
                        return {
                            'error': True,
                            'message': 'Failed to refresh Roller token after expiration',
                            'retry_count': retry_count
                        }
                    
                    # Update token for next retry
                    api_token = new_token
                    retry_count += 1
                    logger.info(f"Retrying booking creation with new token (attempt {retry_count})")
                    continue
                
                # Success or non-token error
                print("This is text xxx === " , roller_response)
                return roller_response
                
            except Exception as e:
                logger.error(f"Error in _create_roller_booking_with_retry: {str(e)}")
                return {
                    'error': True,
                    'message': str(e),
                    'retry_count': retry_count
                }
        
        return {
            'error': True,
            'message': 'Failed to create booking in Roller after maximum retries',
            'retry_count': retry_count
        }
    
    def _is_token_expired_error(self, roller_response):
        """
        Check if the Roller API response indicates a token expired error
        """
        if not roller_response or not isinstance(roller_response, dict):
            return False
        
        # Check for token expired error messages
        if roller_response.get('code') == 'token_not_valid':
            return True
        
        if 'Token is expired' in str(roller_response.get('messages', [])):
            return True
        
        if 'detail' in roller_response and 'token' in roller_response['detail'].lower() and 'expired' in roller_response['detail'].lower():
            return True
        
        return False
    
    def _create_roller_booking_sync(self, payload, api_token):
        """
        Create booking in Roller system synchronously
        """
        if not api_token:
            logger.error("No Roller API token provided")
            return {
                'error': True,
                'message': 'No Roller API token provided'
            }
        
        url = "https://api.haveablast.roller.app/bookings"
        
        # Prepare the payload for Roller
        roller_payload = self._prepare_roller_payload(payload)
        print("This is the roller Payload == " , roller_payload)
        if not roller_payload:
            return {
                'error': True,
                'message': 'Failed to prepare Roller payload'
            }
        
        logger.info(f"Prepared Roller payload with {len(roller_payload.get('items', []))} items")
        
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        
        try:
            logger.info(f"Sending booking to Roller API")
            response = requests.post(
                url,
                headers=headers,
                json=roller_payload,
                timeout=30
            )
            print("This is the final error == " , response)
            logger.info(f"Roller booking response status: {response.status_code}")
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"Roller booking created successfully: {response_data.get('id', 'Unknown ID')}")
                return response_data
            elif response.status_code == 201:
                response_data = response.json()
                logger.info(f"Roller booking created successfully (201): {response_data.get('id', 'Unknown ID')}")
                return response_data
            else:
                # Try to parse error response
                try:
                    error_data = response.json()
                    logger.error(f"Roller API Error: {response.status_code} - {json.dumps(error_data)}")
                    return error_data
                except:
                    logger.error(f"Roller API Error: {response.status_code} - {response.text}")
                    return {
                        'error': True,
                        'status_code': response.status_code,
                        'message': response.text
                    }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Roller API: {str(e)}")
            return {
                'error': True,
                'message': str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error calling Roller API: {str(e)}")
            return {
                'error': True,
                'message': str(e)
            }
    
    def _prepare_roller_payload(self, payload):
        """
        Prepare payload for Roller API from our payload format
        """
        # Extract customer details
        customer_detail = payload.get('customer', {})
        booking_date = payload.get('bookingDate', '')
        
        # Validate booking date
        if not booking_date:
            logger.error("No bookingDate found in payload")
            return None
        
        # Check if payload has 'items' or 'products' key
        if 'items' in payload:
            # Payload already has items in Roller format
            items = payload.get('items', [])
            logger.info(f"Found {len(items)} items in payload")
            
            # Ensure all productIds are integers
            for item in items:
                if 'productId' in item:
                    try:
                        item['productId'] = int(item['productId'])
                    except (ValueError, TypeError) as e:
                        logger.warning(f"Cannot convert productId {item.get('productId')} to integer: {e}")
                
                # Ensure partyPackageInclusions have integer productIds if they exist
                if 'partyPackageInclusions' in item:
                    for inclusion in item['partyPackageInclusions']:
                        if 'productId' in inclusion:
                            try:
                                inclusion['productId'] = int(inclusion['productId'])
                            except (ValueError, TypeError) as e:
                                logger.warning(f"Cannot convert inclusion productId {inclusion.get('productId')} to integer: {e}")
            
        elif 'products' in payload:
            # Legacy format with 'products' - convert to Roller format
            items = self._convert_products_to_items(payload)
            logger.info(f"Converted {len(payload.get('products', []))} products to {len(items)} items")
        else:
            logger.error("Payload must contain either 'items' or 'products'")
            return None
        
        # Validate items
        if not items:
            logger.error("No items found in payload")
            return None
        
        # Check if first item has bookingDate, if not add it
        for item in items:
            if 'bookingDate' not in item:
                item['bookingDate'] = booking_date
        
        # Create Roller payload
        roller_payload = {
            "externalId": payload.get('externalId', f"PD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{payload.get('client_id', '1')}"),
            "bookingDate": booking_date,
            "items": items,
            "customer": {
                "email": customer_detail.get('Email', ''),
                "phone": customer_detail.get('Phone', ''),
                "firstName": customer_detail.get('first_name', ''),
                "lastName": customer_detail.get('LastName', '')
            },
            "comments": payload.get('comments', ''),
            "sendConfirmations": False
        }
        
        # Optional fields
        if 'name' in payload:
            roller_payload['name'] = payload['name']
        
        if 'purchaseDate' in payload:
            roller_payload['purchaseDate'] = payload['purchaseDate']
        
        if 'capacityReservationId' in payload:
            roller_payload['capacityReservationId'] = payload['capacityReservationId']
        
        if 'companyId' in payload:
            try:
                roller_payload['companyId'] = int(payload['companyId'])
            except (ValueError, TypeError) as e:
                logger.warning(f"Cannot convert companyId {payload.get('companyId')} to integer: {e}")
        
        logger.debug(f"Final Roller payload prepared")
        return roller_payload
    
    def _convert_products_to_items(self, payload):
        """
        Convert legacy 'products' format to Roller 'items' format
        """
        products = payload.get('products', [])
        booking_date = payload.get('bookingDate', '')
        items = []
        
        for product in products:
            try:
                product_id = int(product.get('productId', 0))
            except (ValueError, TypeError):
                logger.warning(f"Invalid productId: {product.get('productId')}")
                continue
                
            item = {
                "productId": product_id,
                "quantity": product.get('quantity', 1),
                "bookingDate": product.get('bookingDate', booking_date),
                "startTime": product.get('startTime', '14:00')
            }
            
            # Add priceOverride if present
            if 'priceOverride' in product:
                item['priceOverride'] = product['priceOverride']
            
            # Check if this is a main package with inclusions
            if product.get('packageProductId', 0) > 0:
                # This is a main package - we need to find its inclusions
                package_product_id = product.get('packageProductId')
                
                # Find all products marked as inclusions for this package
                inclusion_products = []
                for other_product in products:
                    if other_product.get('inclusion', False) and other_product.get('packageProductId') == package_product_id:
                        try:
                            inclusion_product_id = int(other_product.get('productId', 0))
                            inclusion_item = {
                                "productId": inclusion_product_id,
                                "quantity": other_product.get('quantity', 1)
                            }
                            inclusion_products.append(inclusion_item)
                        except (ValueError, TypeError):
                            logger.warning(f"Invalid inclusion productId: {other_product.get('productId')}")
                            continue
                
                if inclusion_products:
                    item["partyPackageInclusions"] = inclusion_products
            
            items.append(item)
        
        return items
    
    def _extract_booking_time(self, payload):
        """Extract booking time from products or items array"""
        # Check for items first
        items = payload.get('items', [])
        if items:
            return items[0].get('startTime', '')
        
        # Check for products (legacy format)
        products = payload.get('products', [])
        if products:
            return products[0].get('startTime', '')
        
        return ''
    
    def _generate_capacity_id(self):
        """Generate capacity reservation ID"""
        return f"CAP{datetime.now().strftime('%Y%m%d%H%M%S')}_{str(uuid.uuid4())[:6].upper()}"


