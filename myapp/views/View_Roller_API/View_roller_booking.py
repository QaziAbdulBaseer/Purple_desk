




from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db import transaction
from django.shortcuts import get_object_or_404
from myapp.model.roller_booking_model import RollerBookingDetails
from myapp.model.customer_details_model import CustomerDetails
from myapp.serializers import RollerBookingDetailsSerializer

class RollerBookingAPI(APIView):
    """
    API for creating, updating, and retrieving roller bookings
    """
    permission_classes = [AllowAny]  # Adjust permissions as needed
    
    def post(self, request):
        """
        Create a new roller booking
        ---
        Request Body:
        {
            "customer": 1,
            "roller_id": "ROLLER123",
            "booking_unique_id": "UNIQUE123",
            "booking_date": "2024-01-15",
            "booking_time": "14:30",
            "capacity_reservation_id": "CAP123",
            "payment_made": true,
            "payload": false
        }
        """
        try:
            with transaction.atomic():
                # Validate customer exists
                customer_id = request.data.get('customer')
                if not customer_id:
                    return Response({
                        'success': False,
                        'message': 'Customer ID is required'
                    }, status=status.HTTP_400_BAD_REQUEST)
                
                try:
                    customer = CustomerDetails.objects.get(pk=customer_id)
                except CustomerDetails.DoesNotExist:
                    return Response({
                        'success': False,
                        'message': f'Customer with ID {customer_id} does not exist'
                    }, status=status.HTTP_404_NOT_FOUND)
                
                # Check for duplicate booking_unique_id if provided
                booking_unique_id = request.data.get('booking_unique_id')
                if booking_unique_id:
                    existing_booking = RollerBookingDetails.objects.filter(
                        booking_unique_id=booking_unique_id
                    ).first()
                    if existing_booking:
                        return Response({
                            'success': False,
                            'message': 'Booking with this unique ID already exists',
                            'booking_id': existing_booking.booking_id
                        }, status=status.HTTP_200_OK)
                
                serializer = RollerBookingDetailsSerializer(data=request.data)
                
                if serializer.is_valid():
                    booking = serializer.save()
                    return Response({
                        'success': True,
                        'message': 'Booking created successfully',
                        'booking_id': booking.booking_id,
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
                'message': 'Error creating booking',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request):
        """
        Get all bookings with filters
        ---
        Query Parameters:
        - customer_id: Filter by customer ID
        - roller_id: Filter by roller ID
        - booking_date: Filter by booking date
        - payment_made: Filter by payment status (true/false)
        - payload: Filter by payload status (true/false)
        - limit: Limit number of results
        - offset: Offset for pagination
        """
        try:
            # Start with all bookings
            bookings = RollerBookingDetails.objects.select_related('customer').all()
            
            # Apply filters if provided
            customer_id = request.query_params.get('customer_id')
            if customer_id:
                bookings = bookings.filter(customer_id=customer_id)
            
            roller_id = request.query_params.get('roller_id')
            if roller_id:
                bookings = bookings.filter(roller_id=roller_id)
            
            booking_date = request.query_params.get('booking_date')
            if booking_date:
                bookings = bookings.filter(booking_date=booking_date)
            
            payment_made = request.query_params.get('payment_made')
            if payment_made is not None:
                bookings = bookings.filter(payment_made=payment_made.lower() == 'true')
            
            payload = request.query_params.get('payload')
            if payload is not None:
                bookings = bookings.filter(payload=payload.lower() == 'true')
            
            # Count before pagination
            total_count = bookings.count()
            
            # Apply pagination
            limit = int(request.query_params.get('limit', 100))
            offset = int(request.query_params.get('offset', 0))
            bookings = bookings[offset:offset + limit]
            
            serializer = RollerBookingDetailsSerializer(bookings, many=True)
            
            # Enhanced response with customer details
            data_with_customer_info = []
            for booking_data in serializer.data:
                try:
                    customer = CustomerDetails.objects.get(pk=booking_data['customer'])
                    booking_data['customer_details'] = {
                        'customer_id': customer.customer_id,
                        'email': customer.customer_email,
                        'phone': customer.phone_number,
                        'full_name': f"{customer.first_name} {customer.last_name}"
                    }
                except CustomerDetails.DoesNotExist:
                    booking_data['customer_details'] = None
                
                data_with_customer_info.append(booking_data)
            
            return Response({
                'success': True,
                'total_count': total_count,
                'limit': limit,
                'offset': offset,
                'count': len(data_with_customer_info),
                'data': data_with_customer_info
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error fetching bookings',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RollerBookingDetailAPI(APIView):
    """
    API for single booking operations by ID
    """
    permission_classes = [AllowAny]
    
    def get(self, request, booking_id):
        """
        Get specific booking by ID
        """
        try:
            booking = get_object_or_404(RollerBookingDetails, booking_id=booking_id)
            serializer = RollerBookingDetailsSerializer(booking)
            
            # Add customer details to response
            response_data = serializer.data
            customer = booking.customer
            response_data['customer_details'] = {
                'customer_id': customer.customer_id,
                'email': customer.customer_email,
                'phone': customer.phone_number,
                'full_name': f"{customer.first_name} {customer.last_name}"
            }
            
            return Response({
                'success': True,
                'data': response_data
            }, status=status.HTTP_200_OK)
            
        except RollerBookingDetails.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Booking not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error fetching booking',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, booking_id):
        """
        Update booking details
        ---
        Request Body (partial update allowed):
        {
            "roller_id": "UPDATED123",
            "booking_date": "2024-01-16",
            "payment_made": true,
            "payload": true
        }
        """
        try:
            with transaction.atomic():
                booking = get_object_or_404(RollerBookingDetails, booking_id=booking_id)
                
                # Validate customer if being updated
                if 'customer' in request.data:
                    customer_id = request.data['customer']
                    try:
                        CustomerDetails.objects.get(pk=customer_id)
                    except CustomerDetails.DoesNotExist:
                        return Response({
                            'success': False,
                            'message': f'Customer with ID {customer_id} does not exist'
                        }, status=status.HTTP_404_NOT_FOUND)
                
                # Check for duplicate booking_unique_id if being updated
                if 'booking_unique_id' in request.data:
                    new_unique_id = request.data['booking_unique_id']
                    if new_unique_id and new_unique_id != booking.booking_unique_id:
                        existing = RollerBookingDetails.objects.filter(
                            booking_unique_id=new_unique_id
                        ).exclude(booking_id=booking_id).first()
                        if existing:
                            return Response({
                                'success': False,
                                'message': 'Booking with this unique ID already exists'
                            }, status=status.HTTP_400_BAD_REQUEST)
                
                serializer = RollerBookingDetailsSerializer(booking, data=request.data, partial=True)
                
                if serializer.is_valid():
                    updated_booking = serializer.save()
                    
                    # Prepare response with customer details
                    response_data = serializer.data
                    customer = updated_booking.customer
                    response_data['customer_details'] = {
                        'customer_id': customer.customer_id,
                        'email': customer.customer_email,
                        'phone': customer.phone_number,
                        'full_name': f"{customer.first_name} {customer.last_name}"
                    }
                    
                    return Response({
                        'success': True,
                        'message': 'Booking updated successfully',
                        'data': response_data
                    }, status=status.HTTP_200_OK)
                
                return Response({
                    'success': False,
                    'message': 'Validation error',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except RollerBookingDetails.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Booking not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error updating booking',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def delete(self, request, booking_id):
        """
        Delete a booking
        """
        try:
            booking = get_object_or_404(RollerBookingDetails, booking_id=booking_id)
            
            # Store booking info before deletion
            booking_info = {
                'booking_id': booking.booking_id,
                'customer_id': booking.customer_id if booking.customer else None,
                'roller_id': booking.roller_id,
                'booking_unique_id': booking.booking_unique_id
            }
            
            booking.delete()
            
            return Response({
                'success': True,
                'message': 'Booking deleted successfully',
                'deleted_booking': booking_info
            }, status=status.HTTP_200_OK)
            
        except RollerBookingDetails.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Booking not found'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error deleting booking',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class RollerBookingSearchAPI(APIView):
    """
    API for advanced booking search
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        """
        Search bookings with multiple criteria
        ---
        Request Body:
        {
            "customer_emails": ["john@example.com", "jane@example.com"],
            "date_from": "2024-01-01",
            "date_to": "2024-01-31",
            "payment_status": true,
            "min_booking_id": 100,
            "max_booking_id": 200
        }
        """
        try:
            bookings = RollerBookingDetails.objects.select_related('customer').all()
            
            # Customer emails filter
            customer_emails = request.data.get('customer_emails')
            if customer_emails and isinstance(customer_emails, list):
                bookings = bookings.filter(
                    customer__customer_email__in=customer_emails
                )
            
            # Date range filter
            date_from = request.data.get('date_from')
            date_to = request.data.get('date_to')
            if date_from:
                bookings = bookings.filter(booking_date__gte=date_from)
            if date_to:
                bookings = bookings.filter(booking_date__lte=date_to)
            
            # Payment status filter
            payment_status = request.data.get('payment_status')
            if payment_status is not None:
                bookings = bookings.filter(payment_made=payment_status)
            
            # Booking ID range filter
            min_booking_id = request.data.get('min_booking_id')
            max_booking_id = request.data.get('max_booking_id')
            if min_booking_id:
                bookings = bookings.filter(booking_id__gte=min_booking_id)
            if max_booking_id:
                bookings = bookings.filter(booking_id__lte=max_booking_id)
            
            # Roller IDs filter
            roller_ids = request.data.get('roller_ids')
            if roller_ids and isinstance(roller_ids, list):
                bookings = bookings.filter(roller_id__in=roller_ids)
            
            serializer = RollerBookingDetailsSerializer(bookings, many=True)
            
            return Response({
                'success': True,
                'count': bookings.count(),
                'data': serializer.data
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error searching bookings',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



