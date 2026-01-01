





import requests
import os
from django.conf import settings
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from myapp.model.customer_details_model import CustomerDetails
from myapp.model.locations_model import Location  # Assuming you have a Location model
from myapp.serializers import CustomerDetailsSerializer
from myapp.utils.roller_token_manager import get_or_refresh_roller_token

class CustomerDetailsAPI(APIView):
    permission_classes = [AllowAny]  # Adjust permissions as needed
    
    def post(self, request):
        """
        Create a new customer
        Expected JSON data:
        {
            "customer_email": "john@example.com",
            "phone_number": "1234567890",
            "first_name": "John",
            "last_name": "Doe",
            "roller_customer_id": "ROLLER123"
        }
        """
        try:
            # Check if customer with email already exists
            customer_email = request.data.get('customer_email')
            if customer_email:
                existing_customer = CustomerDetails.objects.filter(
                    customer_email=customer_email
                ).first()
                if existing_customer:
                    return Response({
                        'success': False,
                        'message': 'Customer with this email already exists',
                        'customer_id': existing_customer.customer_id
                    }, status=status.HTTP_200_OK)
            
            serializer = CustomerDetailsSerializer(data=request.data)
            
            if serializer.is_valid():
                customer = serializer.save()
                return Response({
                    'success': True,
                    'message': 'Customer created successfully',
                    'customer_id': customer.customer_id,
                    'data': serializer.data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error creating customer',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """
        Get all customers or filter by parameters
        Query parameters: email, phone, customer_id, location_id
        
        If searching by phone and not found in database, 
        search Roller API and save to database.
        """
        try:
            email = request.query_params.get('email')
            phone = request.query_params.get('phone')
            customer_id = request.query_params.get('customer_id')
            location_id = request.query_params.get('location_id')
            
            customers = CustomerDetails.objects.all()
            
            if email:
                customers = customers.filter(customer_email=email)
            
            if phone:
                # Clean the phone number for searching
                clean_phone = ''.join(filter(str.isdigit, phone))
                customers = customers.filter(phone_number=clean_phone)
                
                # If customers found in database, return them
                if customers.exists():
                    serializer = CustomerDetailsSerializer(customers, many=True)
                    return Response({
                        'success': True,
                        'count': customers.count(),
                        'data': serializer.data
                    }, status=status.HTTP_200_OK)
                
                # If no customers found in database, search Roller API
                else:
                    # Get location for API token - use location_id field instead of id
                    if location_id:
                        try:
                            # Use location_id field as shown in the error message
                            location = Location.objects.get(location_id=location_id)
                        except Location.DoesNotExist:
                            return Response({
                                'success': False,
                                'message': f'Location with ID {location_id} not found'
                            }, status=status.HTTP_404_NOT_FOUND)
                    else:
                        # Get default location or first available location
                        # You can change this logic based on your requirements
                        location = Location.objects.filter(
                            roller_client_id__isnull=False,
                            roller_client_secret__isnull=False
                        ).first()
                        
                        if not location:
                            return Response({
                                'success': False,
                                'message': 'No location configured with Roller API credentials'
                            }, status=status.HTTP_400_BAD_REQUEST)
                    
                    # Get or refresh Roller API token
                    access_token = get_or_refresh_roller_token(location)
                    print("Access Token:", access_token)  # Debugging line
                    if not access_token:
                        return Response({
                            'success': False,
                            'message': 'Failed to obtain Roller API token. Check location credentials.'
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    
                    # Step 1: Search Roller API bookings to get customer ID
                    roller_base_url = getattr(settings, 'ROLLER_BASE_URL', 'https://api.haveablast.roller.app')
                    
                    # Clean phone number (remove spaces, dashes, parentheses, etc.)
                    clean_phone = ''.join(filter(str.isdigit, phone))
                    clean_phone = phone
                    
                    # Search for bookings with this phone number
                    search_url = f"{roller_base_url}/bookings"
                    headers = {
                        'Accept': 'application/json',
                        'Authorization': f'Bearer {access_token}'
                    }
                    params = {'keywords': clean_phone}
                    
                    try:
                        # Search for bookings with this phone number
                        search_response = requests.get(search_url, headers=headers, params=params, timeout=30)
                        
                        if search_response.status_code == 401:
                            # Token might be expired, try to refresh and retry
                            # Update the token manager to accept force_refresh parameter
                            access_token = get_or_refresh_roller_token(location)
                            if access_token:
                                headers['Authorization'] = f'Bearer {access_token}'
                                search_response = requests.get(search_url, headers=headers, params=params, timeout=30)
                        
                        search_response.raise_for_status()
                        bookings_data = search_response.json()
                        
                        if not bookings_data.get('bookings'):
                            return Response({
                                'success': False,
                                'message': 'Customer not found in database or Roller API'
                            }, status=status.HTTP_404_NOT_FOUND)
                        
                        # Get customer ID from the first booking
                        roller_customer_id = None
                        for booking in bookings_data.get('bookings', []):
                            if booking.get('customerId'):
                                roller_customer_id = booking.get('customerId')
                                break
                        
                        if not roller_customer_id:
                            return Response({
                                'success': False,
                                'message': 'Customer ID not found in Roller bookings'
                            }, status=status.HTTP_404_NOT_FOUND)
                        
                        # Step 2: Get customer details from Roller API using the customer ID
                        guest_url = f"{roller_base_url}/guests/{roller_customer_id}"
                        guest_response = requests.get(guest_url, headers=headers, timeout=30)
                        
                        if guest_response.status_code == 401:
                            # Token might be expired, try to refresh and retry
                            access_token = get_or_refresh_roller_token(location)
                            if access_token:
                                headers['Authorization'] = f'Bearer {access_token}'
                                guest_response = requests.get(guest_url, headers=headers, timeout=30)
                        
                        guest_response.raise_for_status()
                        guest_data = guest_response.json()
                        
                        # Check if we already have this customer by roller_customer_id
                        existing_customer = CustomerDetails.objects.filter(
                            roller_customer_id=roller_customer_id
                        ).first()
                        
                        if existing_customer:
                            # Customer already exists in our database
                            serializer = CustomerDetailsSerializer(existing_customer)
                            return Response({
                                'success': True,
                                'count': 1,
                                'data': [serializer.data]
                            }, status=status.HTTP_200_OK)
                        
                        # Map Roller API data to our model
                        customer_data = {
                            'customer_email': guest_data.get('email'),
                            'phone_number': guest_data.get('phone'),
                            'first_name': guest_data.get('firstName'),
                            'last_name': guest_data.get('lastName'),
                            'roller_customer_id': roller_customer_id,
                        }
                        
                        # Add optional fields if they exist
                        optional_fields = {
                            'date_of_birth': guest_data.get('dateOfBirth'),
                            'gender': guest_data.get('gender'),
                            'accept_marketing': guest_data.get('acceptMarketing'),
                            'accept_marketing_sms': guest_data.get('acceptMarketingSms'),
                            'tax_identification_number': guest_data.get('taxIdentificationNumber'),
                        }
                        
                        # Only add fields that are not None
                        for field, value in optional_fields.items():
                            if value is not None:
                                customer_data[field] = value
                        
                        # Save address if exists
                        address = guest_data.get('address')
                        if address:
                            address_fields = {
                                'street': address.get('street'),
                                'suburb': address.get('suburb'),
                                'city': address.get('city'),
                                'state': address.get('state'),
                                'postcode': address.get('postcode'),
                                'country': address.get('country'),
                            }
                            # Only add address fields that are not None
                            for field, value in address_fields.items():
                                if value is not None:
                                    customer_data[field] = value
                        
                        # Save to database
                        serializer = CustomerDetailsSerializer(data=customer_data)
                        if serializer.is_valid():
                            customer = serializer.save()
                            # Return single customer data in the same format
                            return Response({
                                'success': True,
                                'count': 1,
                                'data': [serializer.data]
                            }, status=status.HTTP_200_OK)
                        else:
                            # Even if serializer fails, we can return the Roller API data
                            # But log the error
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Error saving customer from Roller API: {serializer.errors}")
                            
                            # Return basic customer info from Roller API
                            roller_customer_data = {
                                'customer_email': guest_data.get('email'),
                                'phone_number': guest_data.get('phone'),
                                'first_name': guest_data.get('firstName'),
                                'last_name': guest_data.get('lastName'),
                                'roller_customer_id': roller_customer_id,
                                'date_of_birth': guest_data.get('dateOfBirth'),
                                'gender': guest_data.get('gender'),
                                'source': 'roller_api_not_saved'
                            }
                            
                            # Remove None values
                            roller_customer_data = {k: v for k, v in roller_customer_data.items() if v is not None}
                            
                            return Response({
                                'success': True,
                                'count': 1,
                                'data': [roller_customer_data],
                                'warning': 'Customer found in Roller API but could not save to local database'
                            }, status=status.HTTP_200_OK)
                        
                    except requests.exceptions.RequestException as e:
                        error_msg = f'Error connecting to Roller API: {str(e)}'
                        if hasattr(e, 'response') and e.response is not None:
                            error_msg += f' - Status: {e.response.status_code} - Response: {e.response.text[:200]}'
                        
                        return Response({
                            'success': False,
                            'message': error_msg
                        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
                    except Exception as e:
                        return Response({
                            'success': False,
                            'message': f'Error processing Roller API response: {str(e)}'
                        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if customer_id:
                customers = customers.filter(customer_id=customer_id)
            
            # For non-phone searches or when phone found in DB
            serializer = CustomerDetailsSerializer(customers, many=True)
            
            return Response({
                'success': True,
                'count': customers.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error fetching customers',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CustomerDetailByID(APIView):
    permission_classes = [AllowAny]  # Adjust permissions as needed
    
    def get(self, request, customer_id):
        """
        Get customer by ID
        """
        try:
            customer = CustomerDetails.objects.get(customer_id=customer_id)
            serializer = CustomerDetailsSerializer(customer)
            
            return Response({
                'success': True,
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except CustomerDetails.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error fetching customer',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, customer_id):
        """
        Update customer details
        """
        try:
            customer = CustomerDetails.objects.get(customer_id=customer_id)
            serializer = CustomerDetailsSerializer(customer, data=request.data, partial=True)
            
            if serializer.is_valid():
                serializer.save()
                return Response({
                    'success': True,
                    'message': 'Customer updated successfully',
                    'data': serializer.data
                }, status=status.HTTP_200_OK)
            
            return Response({
                'success': False,
                'message': 'Validation error',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
        except CustomerDetails.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Customer not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error updating customer',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




