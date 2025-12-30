# hi i want you create 2 new tables. 1) customers_details 2) booking_details

# user give give one payload and we have to store data in both tables.
# The payload is like this === 

# {
#   "products": [
#     {
#       "productId": "423284",
#       "packageProductId": 1,
#       "quantity": 20,
#       "startTime": "17:00"
#     },
#     {
#       "productId": 423263,
#       "packageProductId": 1,
#       "quantity": 1,
#       "startTime": "17:00",
#       "inclusion": true
#     },
#     {
#       "productId": 423250,
#       "packageProductId": 0,
#       "quantity": 2,
#       "startTime": "17:00",
#       "inclusion": true
#     },
#     {
#       "productId": 423249,
#       "packageProductId": 0,
#       "quantity": 1,
#       "startTime": "17:00",
#       "inclusion": true
#     },
#     {
#       "productId": 423251,
#       "packageProductId": 0,
#       "quantity": 1,
#       "startTime": "17:00",
#       "inclusion": true
#     },
#     {
#       "productId": 423426,
#       "packageProductId": 0,
#       "quantity": 2,
#       "startTime": "17:00",
#       "inclusion": true
#     },
#     {
#       "productId": 423432,
#       "packageProductId": 0,
#       "quantity": 2,
#       "startTime": "17:00",
#       "inclusion": true
#     }
#   ],
#   "customerDetail": {
#     "customer_email": "abdullah.shahid1045@gmail.com",
#     "phone_number": "3148272430",
#     "first_name": "Ali",
#     "last_name": "Hassan"
#   },
#   "client_id": 10,
#   "bookingDate": "2026-01-10",
#   "comments": "Guest of honor: Jacob",
#   "fullPay": false,
#   "depositPercentage": 0.0,
#   "depositAmount": null
# }


# so we have to store the customerDetail part in customers_details table and rest of the data in booking_details table.

# but also give the customer id from customers_details table as foreign key in booking_details table.
# and if customer already exists in customers_details table based on email then we dont have to create new record in customers_details table rather we have to use the existing customer id in booking_details table.

# but before inserting the data in both tables we have to Create draft booking in roller system using roller api.

# this is all the detail about the roller draft booking api

# views/View_Roller_API/View_Product_Availability.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from datetime import datetime
import logging
import requests
from django.utils import timezone

from myapp.model.locations_model import Location

logger = logging.getLogger(__name__)

class ProductAvailabilityAPIView(APIView):
    """
    API to check product availability and capacity
    Gets credentials directly from Location table
    """
    
    def get_roller_token(self, location):
        """
        Get Roller token for a location.
        If token exists and is not expired, return it.
        If expired or doesn't exist, fetch new token and save it.
        """
        # Check if token exists and is not expired
        if not location.is_token_expired() and location.roller_access_token:
            return location.roller_access_token
        
        # Check if we have credentials
        if not location.roller_client_id or not location.roller_client_secret:
            logger.warning(f"Location {location.location_name} has no Roller API credentials")
            return None
        
        # Fetch new token
        url = "https://api.haveablast.roller.app/token"
        payload = {
            "client_id": location.roller_client_id,
            "client_secret": location.roller_client_secret
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")
            
            if access_token:
                # Save token to location
                location.roller_access_token = access_token
                location.roller_token_created_at = timezone.now()
                location.save(update_fields=['roller_access_token', 'roller_token_created_at'])
                logger.info(f"New token obtained for location {location.location_name}")
                return access_token
            else:
                logger.error(f"No access token in response for location {location.location_name}")
                return None
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting token for location {location.location_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing token response for location {location.location_name}: {str(e)}")
            return None
    
    def get_product_availability(self, product_id, date, product_category, api_token):
        """Get availability from Roller API"""
        url = "https://api.haveablast.roller.app/product-availability"
        headers = {
            "Accept": "application/json",
            "Authorization": f"Bearer {api_token}"
        }
        
        # Format date
        if isinstance(date, datetime):
            date_str = date.strftime("%Y-%m-%d")
        else:
            date_str = str(date)
        
        params = {
            "ProductIds": str(product_id),
            "Date": date_str,
            "ProductCategory": product_category,
        }
        
        try:
            response = requests.get(url, headers=headers, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error getting availability: {str(e)}")
            return None
    
    def get_available_slots(self, product_id, date, product_category, api_token):
        """Parse available slots from response"""
        resp = self.get_product_availability(product_id, date, product_category, api_token)
        if not resp:
            return [], {}
        
        entries = resp if isinstance(resp, list) else resp.get("data") or [resp]
        pid_str = str(product_id)
        slots = []
        availability = {}
        
        for entry in entries:
            if not isinstance(entry, dict):
                continue
            
            sessions = entry.get("sessions", [])
            
            for s in sessions:
                start_time = s.get("startTime")
                if not start_time:
                    continue
                
                # Convert to AM/PM
                try:
                    start_time_ampm = datetime.strptime(start_time, "%H:%M").strftime("%I:%M %p")
                except:
                    start_time_ampm = start_time
                
                # Find capacity
                cap = None
                for alloc in s.get("allocations", []):
                    if str(alloc.get("productId")) == pid_str:
                        cap = (
                            alloc.get("bookableCapacityRemaining")
                            or alloc.get("ticketCapacityRemaining")
                        )
                        break
                
                if cap is None:
                    cap = s.get("ticketCapacityRemaining") or s.get("bookableCapacityRemaining")
                
                if isinstance(cap, (int, float)) and cap > 0:
                    slots.append(start_time_ampm)
                    availability[start_time_ampm] = int(cap)
        
        return slots, availability
    
    def get(self, request):
        """
        Handle GET request for product availability
        Expected parameters:
        - date (required): YYYY-MM-DD
        - client_id (required): Location ID (uses location_id from Location table)
        - product_id (optional): Override location's default product_id
        - category_name (optional): Override location's default category
        - quantity (optional): Number of jumpers
        - time (optional): Specific time slot (HH:MM format)
        """
        # Extract parameters
        date = request.GET.get('date')
        client_id = request.GET.get('client_id')  # This is location_id
        product_id = request.GET.get('product_id')
        category_name = request.GET.get('category_name')
        quantity = request.GET.get('quantity')
        time_str = request.GET.get('time')
        
        # Validate required parameters
        if not date:
            return Response({
                "status": "error",
                "message": "Date parameter is required",
                "data": {"availability": "Unavailable"}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not client_id:
            return Response({
                "status": "error",
                "message": "client_id parameter is required (Location ID)",
                "data": {"availability": "Unavailable"}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Parse date
            date_obj = datetime.strptime(date, "%Y-%m-%d").date()
        except ValueError:
            return Response({
                "status": "error",
                "message": "Invalid date format. Use YYYY-MM-DD",
                "data": {"availability": "Unavailable"}
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Parse quantity if provided
        if quantity:
            try:
                quantity = int(quantity)
                if quantity <= 0:
                    raise ValueError
            except ValueError:
                return Response({
                    "status": "error",
                    "message": "Quantity must be a positive integer",
                    "data": {"availability": "Unavailable"}
                }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Get location - ONLY USE THE SPECIFIED LOCATION ID
            try:
                location = Location.objects.get(location_id=client_id)
                logger.info(f"Found location ID {client_id}: {location.location_name}")
            except Location.DoesNotExist:
                logger.error(f"Location with ID {client_id} not found")
                return Response({
                    "status": "error",
                    "message": f"Location with ID {client_id} not found",
                    "data": {"availability": "Unavailable"}
                }, status=status.HTTP_404_NOT_FOUND)
            
            # CRITICAL FIX: Check if location has Roller credentials
            # Don't fall back to any other location - strictly use only this location
            if not location.roller_client_id or not location.roller_client_secret:
                logger.error(f"Location {location.location_name} (ID: {client_id}) does not have Roller API credentials configured")
                return Response({
                    "status": "error",
                    "message": f"Location {location.location_name} does not have Roller API credentials configured",
                    "data": {"availability": "Unavailable"}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get token - this will only use the specified location's credentials
            api_token = self.get_roller_token(location)
            if not api_token:
                logger.error(f"Failed to get API access token for location {location.location_name}")
                return Response({
                    "status": "error",
                    "message": f"Failed to get API access token for location {location.location_name}",
                    "data": {"availability": "Unavailable"}
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Determine product_id to use
            if product_id:
                try:
                    current_product_id = int(product_id)
                except ValueError:
                    return Response({
                        "status": "error",
                        "message": "Invalid product_id format",
                        "data": {"availability": "Unavailable"}
                    }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # Check if location has a default product_id
                # You might want to add a roller_product_id field to Location model
                # For now, we'll return an error if not provided
                return Response({
                    "status": "error",
                    "message": "product_id parameter is required",
                    "data": {"availability": "Unavailable"}
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Determine category to use
            current_category = category_name if category_name else 'TESTB'
            
            # Check specific time
            if time_str:
                slots, availability = self.get_available_slots(
                    current_product_id, date_obj, current_category, api_token
                )
                
                # Convert time to AM/PM for matching
                try:
                    time_obj = datetime.strptime(time_str, "%H:%M")
                    time_ampm = time_obj.strftime("%I:%M %p")
                except:
                    time_ampm = time_str
                
                cap = availability.get(time_ampm)
                
                if cap is None:
                    return Response({
                        "status": "success",
                        "message": f"Unavailable slot for {time_str}",
                        "data": {
                            "availability": "Unavailable",
                            "depositPercentage": 50,  # Default
                            "depositAmount": None
                        }
                    })
                
                # Check quantity
                if quantity and quantity > cap:
                    return Response({
                        "status": "success",
                        "message": f"Insufficient capacity. Available: {cap}",
                        "data": {
                            "availability": "Unavailable",
                            "depositPercentage": 50,
                            "depositAmount": None
                        }
                    })
                
                return Response({
                    "status": "success",
                    "message": "success",
                    "data": {
                        "availability": time_str,
                        "depositPercentage": 50,
                        "depositAmount": None,
                        "capacity": cap
                    }
                })
            
            # Get all slots
            slots, availability = self.get_available_slots(
                current_product_id, date_obj, current_category, api_token
            )
            
            # Filter by quantity if provided
            if quantity:
                filtered_slots = []
                for slot, cap in availability.items():
                    if quantity <= cap:
                        filtered_slots.append(slot)
                
                if not filtered_slots:
                    return Response({
                        "status": "success",
                        "message": "No available slots for requested quantity",
                        "data": {
                            "availability": "Unavailable",
                            "depositPercentage": 50,
                            "depositAmount": None
                        }
                    })
                
                return Response({
                    "status": "success",
                    "message": "success",
                    "data": {
                        "availability": ", ".join(filtered_slots),
                        "depositPercentage": 50,
                        "depositAmount": None,
                        "totalSlots": len(filtered_slots)
                    }
                })
            
            # Return all slots
            if not slots:
                return Response({
                    "status": "success",
                    "message": "No available slots",
                    "data": {
                        "availability": "Unavailable",
                        "depositPercentage": 50,
                        "depositAmount": None
                    }
                })
            
            return Response({
                "status": "success",
                "message": "success",
                "data": {
                    "availability": ", ".join(slots),
                    "depositPercentage": 50,
                    "depositAmount": None,
                    "totalSlots": len(slots)
                }
            })
            
        except Exception as e:
            logger.exception(f"Unexpected error in availability check: {str(e)}")
            return Response({
                "status": "error",
                "message": f"Internal server error: {str(e)}",
                "data": {"availability": "Unavailable"}
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



