

# # # hi see that code I want that response will retun the time in the 

# # # 24 hours formate. that 

# # # now like that ({
# # #     "status": "success",
# # #     "message": "success",
# # #     "data": {
# # #         "availability": "04:00 PM, 05:15 PM",
# # #         "depositPercentage": 50,
# # #         "depositAmount": null,
# # #         "totalSlots": 2
# # #     }
# # # })

# # # I need the availability time in 24 hours time formate.

# # # and i also need one more update. and that update like i need all time the availability slots 
# # # i will explan if a user searh for (01/05/2026) and its retrun an answer  like that = "availability": "04:00 PM, 05:15 PM",

# # # but if i search for ((01/05/2026) )  and 11:00 then its return like that == 

# # # {
# # #     "status": "success",
# # #     "message": "Unavailable slot for 10:16",
# # #     "data": {
# # #         "availability": "Unavailable",
# # #         "depositPercentage": 50,
# # #         "depositAmount": null
# # #     }
# # # }


# # # but i want you still how all the availability_slots make a new key value pair that just how the all availabile slot of search date
# # # so its like  that === 
# # # {
# # #     "status": "success",
# # #     "message": "Unavailable slot for 10:16",
# # #     "data": {
# # #         "availability": "Unavailable",
# # #         "availability_slots" : "04:00 PM, 05:15 PM",
# # #         "depositPercentage": 50,
# # #         "depositAmount": null
# # #     }
# # # }
# # # views/View_Roller_API/View_Product_Availability.py
# # from rest_framework.views import APIView
# # from rest_framework.response import Response
# # from rest_framework import status
# # from datetime import datetime
# # import logging
# # import requests
# # from django.utils import timezone

# # from myapp.model.locations_model import Location

# # logger = logging.getLogger(__name__)

# # class ProductAvailabilityAPIView(APIView):
# #     """
# #     API to check product availability and capacity
# #     Gets credentials directly from Location table
# #     """
    
# #     def get_roller_token(self, location):
# #         """
# #         Get Roller token for a location.
# #         If token exists and is not expired, return it.
# #         If expired or doesn't exist, fetch new token and save it.
# #         """
# #         # Check if token exists and is not expired
# #         if not location.is_token_expired() and location.roller_access_token:
# #             return location.roller_access_token
        
# #         # Check if we have credentials
# #         if not location.roller_client_id or not location.roller_client_secret:
# #             logger.warning(f"Location {location.location_name} has no Roller API credentials")
# #             return None
        
# #         # Fetch new token
# #         url = "https://api.haveablast.roller.app/token"
# #         payload = {
# #             "client_id": location.roller_client_id,
# #             "client_secret": location.roller_client_secret
# #         }
# #         headers = {
# #             "Content-Type": "application/json",
# #             "Accept": "application/json",
# #         }
        
# #         try:
# #             response = requests.post(url, json=payload, headers=headers, timeout=30)
# #             response.raise_for_status()
# #             data = response.json()
# #             access_token = data.get("access_token")
            
# #             if access_token:
# #                 # Save token to location
# #                 location.roller_access_token = access_token
# #                 location.roller_token_created_at = timezone.now()
# #                 location.save(update_fields=['roller_access_token', 'roller_token_created_at'])
# #                 logger.info(f"New token obtained for location {location.location_name}")
# #                 return access_token
# #             else:
# #                 logger.error(f"No access token in response for location {location.location_name}")
# #                 return None
                
# #         except requests.exceptions.RequestException as e:
# #             logger.error(f"Error getting token for location {location.location_name}: {str(e)}")
# #             return None
# #         except Exception as e:
# #             logger.error(f"Error processing token response for location {location.location_name}: {str(e)}")
# #             return None
    
# #     def get_product_availability(self, product_id, date, product_category, api_token):
# #         """Get availability from Roller API"""
# #         url = "https://api.haveablast.roller.app/product-availability"
# #         headers = {
# #             "Accept": "application/json",
# #             "Authorization": f"Bearer {api_token}"
# #         }
        
# #         # Format date
# #         if isinstance(date, datetime):
# #             date_str = date.strftime("%Y-%m-%d")
# #         else:
# #             date_str = str(date)
        
# #         params = {
# #             "ProductIds": str(product_id),
# #             "Date": date_str,
# #             "ProductCategory": product_category,
# #         }
        
# #         try:
# #             response = requests.get(url, headers=headers, params=params, timeout=30)
# #             response.raise_for_status()
# #             return response.json()
# #         except Exception as e:
# #             logger.error(f"Error getting availability: {str(e)}")
# #             return None
    
# #     def get_available_slots(self, product_id, date, product_category, api_token):
# #         """Parse available slots from response"""
# #         resp = self.get_product_availability(product_id, date, product_category, api_token)
# #         if not resp:
# #             return [], {}
        
# #         entries = resp if isinstance(resp, list) else resp.get("data") or [resp]
# #         pid_str = str(product_id)
# #         slots = []
# #         availability = {}
        
# #         for entry in entries:
# #             if not isinstance(entry, dict):
# #                 continue
            
# #             sessions = entry.get("sessions", [])
            
# #             for s in sessions:
# #                 start_time = s.get("startTime")
# #                 if not start_time:
# #                     continue
                
# #                 # Convert to AM/PM
# #                 try:
# #                     start_time_ampm = datetime.strptime(start_time, "%H:%M").strftime("%I:%M %p")
# #                 except:
# #                     start_time_ampm = start_time
                
# #                 # Find capacity
# #                 cap = None
# #                 for alloc in s.get("allocations", []):
# #                     if str(alloc.get("productId")) == pid_str:
# #                         cap = (
# #                             alloc.get("bookableCapacityRemaining")
# #                             or alloc.get("ticketCapacityRemaining")
# #                         )
# #                         break
                
# #                 if cap is None:
# #                     cap = s.get("ticketCapacityRemaining") or s.get("bookableCapacityRemaining")
                
# #                 if isinstance(cap, (int, float)) and cap > 0:
# #                     slots.append(start_time_ampm)
# #                     availability[start_time_ampm] = int(cap)
        
# #         return slots, availability
    
# #     def get(self, request):
# #         """
# #         Handle GET request for product availability
# #         Expected parameters:
# #         - date (required): YYYY-MM-DD
# #         - client_id (required): Location ID (uses location_id from Location table)
# #         - product_id (optional): Override location's default product_id
# #         - category_name (optional): Override location's default category
# #         - quantity (optional): Number of jumpers
# #         - time (optional): Specific time slot (HH:MM format)
# #         """
# #         # Extract parameters
# #         date = request.GET.get('date')
# #         client_id = request.GET.get('client_id')  # This is location_id
# #         product_id = request.GET.get('product_id')
# #         category_name = request.GET.get('category_name')
# #         quantity = request.GET.get('quantity')
# #         time_str = request.GET.get('time')
        
# #         # Validate required parameters
# #         if not date:
# #             return Response({
# #                 "status": "error",
# #                 "message": "Date parameter is required",
# #                 "data": {"availability": "Unavailable"}
# #             }, status=status.HTTP_400_BAD_REQUEST)
        
# #         if not client_id:
# #             return Response({
# #                 "status": "error",
# #                 "message": "client_id parameter is required (Location ID)",
# #                 "data": {"availability": "Unavailable"}
# #             }, status=status.HTTP_400_BAD_REQUEST)
        
# #         try:
# #             # Parse date
# #             date_obj = datetime.strptime(date, "%Y-%m-%d").date()
# #         except ValueError:
# #             return Response({
# #                 "status": "error",
# #                 "message": "Invalid date format. Use YYYY-MM-DD",
# #                 "data": {"availability": "Unavailable"}
# #             }, status=status.HTTP_400_BAD_REQUEST)
        
# #         # Parse quantity if provided
# #         if quantity:
# #             try:
# #                 quantity = int(quantity)
# #                 if quantity <= 0:
# #                     raise ValueError
# #             except ValueError:
# #                 return Response({
# #                     "status": "error",
# #                     "message": "Quantity must be a positive integer",
# #                     "data": {"availability": "Unavailable"}
# #                 }, status=status.HTTP_400_BAD_REQUEST)
        
# #         try:
# #             # Get location - ONLY USE THE SPECIFIED LOCATION ID
# #             try:
# #                 location = Location.objects.get(location_id=client_id)
# #                 logger.info(f"Found location ID {client_id}: {location.location_name}")
# #             except Location.DoesNotExist:
# #                 logger.error(f"Location with ID {client_id} not found")
# #                 return Response({
# #                     "status": "error",
# #                     "message": f"Location with ID {client_id} not found",
# #                     "data": {"availability": "Unavailable"}
# #                 }, status=status.HTTP_404_NOT_FOUND)
            
# #             # CRITICAL FIX: Check if location has Roller credentials
# #             # Don't fall back to any other location - strictly use only this location
# #             if not location.roller_client_id or not location.roller_client_secret:
# #                 logger.error(f"Location {location.location_name} (ID: {client_id}) does not have Roller API credentials configured")
# #                 return Response({
# #                     "status": "error",
# #                     "message": f"Location {location.location_name} does not have Roller API credentials configured",
# #                     "data": {"availability": "Unavailable"}
# #                 }, status=status.HTTP_400_BAD_REQUEST)
            
# #             # Get token - this will only use the specified location's credentials
# #             api_token = self.get_roller_token(location)
# #             if not api_token:
# #                 logger.error(f"Failed to get API access token for location {location.location_name}")
# #                 return Response({
# #                     "status": "error",
# #                     "message": f"Failed to get API access token for location {location.location_name}",
# #                     "data": {"availability": "Unavailable"}
# #                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
# #             # Determine product_id to use
# #             if product_id:
# #                 try:
# #                     current_product_id = int(product_id)
# #                 except ValueError:
# #                     return Response({
# #                         "status": "error",
# #                         "message": "Invalid product_id format",
# #                         "data": {"availability": "Unavailable"}
# #                     }, status=status.HTTP_400_BAD_REQUEST)
# #             else:
# #                 # Check if location has a default product_id
# #                 # You might want to add a roller_product_id field to Location model
# #                 # For now, we'll return an error if not provided
# #                 return Response({
# #                     "status": "error",
# #                     "message": "product_id parameter is required",
# #                     "data": {"availability": "Unavailable"}
# #                 }, status=status.HTTP_400_BAD_REQUEST)
            
# #             # Determine category to use
# #             current_category = category_name if category_name else 'TESTB'
            
# #             # Check specific time
# #             if time_str:
# #                 slots, availability = self.get_available_slots(
# #                     current_product_id, date_obj, current_category, api_token
# #                 )
                
# #                 # Convert time to AM/PM for matching
# #                 try:
# #                     time_obj = datetime.strptime(time_str, "%H:%M")
# #                     time_ampm = time_obj.strftime("%I:%M %p")
# #                 except:
# #                     time_ampm = time_str
                
# #                 cap = availability.get(time_ampm)
                
# #                 if cap is None:
# #                     return Response({
# #                         "status": "success",
# #                         "message": f"Unavailable slot for {time_str}",
# #                         "data": {
# #                             "availability": "Unavailable",
# #                             "depositPercentage": 50,  # Default
# #                             "depositAmount": None
# #                         }
# #                     })
                
# #                 # Check quantity
# #                 if quantity and quantity > cap:
# #                     return Response({
# #                         "status": "success",
# #                         "message": f"Insufficient capacity. Available: {cap}",
# #                         "data": {
# #                             "availability": "Unavailable",
# #                             "depositPercentage": 50,
# #                             "depositAmount": None
# #                         }
# #                     })
                
# #                 return Response({
# #                     "status": "success",
# #                     "message": "success",
# #                     "data": {
# #                         "availability": time_str,
# #                         "depositPercentage": 50,
# #                         "depositAmount": None,
# #                         "capacity": cap
# #                     }
# #                 })
            
# #             # Get all slots
# #             slots, availability = self.get_available_slots(
# #                 current_product_id, date_obj, current_category, api_token
# #             )
            
# #             # Filter by quantity if provided
# #             if quantity:
# #                 filtered_slots = []
# #                 for slot, cap in availability.items():
# #                     if quantity <= cap:
# #                         filtered_slots.append(slot)
                
# #                 if not filtered_slots:
# #                     return Response({
# #                         "status": "success",
# #                         "message": "No available slots for requested quantity",
# #                         "data": {
# #                             "availability": "Unavailable",
# #                             "depositPercentage": 50,
# #                             "depositAmount": None
# #                         }
# #                     })
                
# #                 return Response({
# #                     "status": "success",
# #                     "message": "success",
# #                     "data": {
# #                         "availability": ", ".join(filtered_slots),
# #                         "depositPercentage": 50,
# #                         "depositAmount": None,
# #                         "totalSlots": len(filtered_slots)
# #                     }
# #                 })
            
# #             # Return all slots
# #             if not slots:
# #                 return Response({
# #                     "status": "success",
# #                     "message": "No available slots",
# #                     "data": {
# #                         "availability": "Unavailable",
# #                         "depositPercentage": 50,
# #                         "depositAmount": None
# #                     }
# #                 })
            
# #             return Response({
# #                 "status": "success",
# #                 "message": "success",
# #                 "data": {
# #                     "availability": ", ".join(slots),
# #                     "depositPercentage": 50,
# #                     "depositAmount": None,
# #                     "totalSlots": len(slots)
# #                 }
# #             })
            
# #         except Exception as e:
# #             logger.exception(f"Unexpected error in availability check: {str(e)}")
# #             return Response({
# #                 "status": "error",
# #                 "message": f"Internal server error: {str(e)}",
# #                 "data": {"availability": "Unavailable"}
# #             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)




# # the availability_slots is working perfect. But still i am getting a a time in am and pm
# # i need the time in 24 hours formate. Kindly update it and write the compleate function 

# # views/View_Roller_API/View_Product_Availability.py
# from rest_framework.views import APIView
# from rest_framework.response import Response
# from rest_framework import status
# from datetime import datetime
# import logging
# import requests
# from django.utils import timezone

# from myapp.model.locations_model import Location

# logger = logging.getLogger(__name__)

# class ProductAvailabilityAPIView(APIView):
#     """
#     API to check product availability and capacity
#     Gets credentials directly from Location table
#     """
    
#     def get_roller_token(self, location):
#         """
#         Get Roller token for a location.
#         If token exists and is not expired, return it.
#         If expired or doesn't exist, fetch new token and save it.
#         """
#         # Check if token exists and is not expired
#         if not location.is_token_expired() and location.roller_access_token:
#             return location.roller_access_token
        
#         # Check if we have credentials
#         if not location.roller_client_id or not location.roller_client_secret:
#             logger.warning(f"Location {location.location_name} has no Roller API credentials")
#             return None
        
#         # Fetch new token
#         url = "https://api.haveablast.roller.app/token"
#         payload = {
#             "client_id": location.roller_client_id,
#             "client_secret": location.roller_client_secret
#         }
#         headers = {
#             "Content-Type": "application/json",
#             "Accept": "application/json",
#         }
        
#         try:
#             response = requests.post(url, json=payload, headers=headers, timeout=30)
#             response.raise_for_status()
#             data = response.json()
#             access_token = data.get("access_token")
            
#             if access_token:
#                 # Save token to location
#                 location.roller_access_token = access_token
#                 location.roller_token_created_at = timezone.now()
#                 location.save(update_fields=['roller_access_token', 'roller_token_created_at'])
#                 logger.info(f"New token obtained for location {location.location_name}")
#                 return access_token
#             else:
#                 logger.error(f"No access token in response for location {location.location_name}")
#                 return None
                
#         except requests.exceptions.RequestException as e:
#             logger.error(f"Error getting token for location {location.location_name}: {str(e)}")
#             return None
#         except Exception as e:
#             logger.error(f"Error processing token response for location {location.location_name}: {str(e)}")
#             return None
    
#     def get_product_availability(self, product_id, date, product_category, api_token):
#         """Get availability from Roller API"""
#         url = "https://api.haveablast.roller.app/product-availability"
#         headers = {
#             "Accept": "application/json",
#             "Authorization": f"Bearer {api_token}"
#         }
        
#         # Format date
#         if isinstance(date, datetime):
#             date_str = date.strftime("%Y-%m-%d")
#         else:
#             date_str = str(date)
        
#         params = {
#             "ProductIds": str(product_id),
#             "Date": date_str,
#             "ProductCategory": product_category,
#         }
        
#         try:
#             response = requests.get(url, headers=headers, params=params, timeout=30)
#             response.raise_for_status()
#             return response.json()
#         except Exception as e:
#             logger.error(f"Error getting availability: {str(e)}")
#             return None
    
#     def get_available_slots(self, product_id, date, product_category, api_token):
#         """Parse available slots from response"""
#         resp = self.get_product_availability(product_id, date, product_category, api_token)
#         if not resp:
#             return [], {}, []
        
#         entries = resp if isinstance(resp, list) else resp.get("data") or [resp]
#         pid_str = str(product_id)
#         slots_24h = []
#         slots_12h = []
#         availability = {}
        
#         for entry in entries:
#             if not isinstance(entry, dict):
#                 continue
            
#             sessions = entry.get("sessions", [])
            
#             for s in sessions:
#                 start_time = s.get("startTime")
#                 if not start_time:
#                     continue
                
#                 # Keep original 24-hour format
#                 start_time_24h = start_time
                
#                 # Convert to AM/PM format
#                 try:
#                     start_time_12h = datetime.strptime(start_time, "%H:%M").strftime("%I:%M %p")
#                 except:
#                     start_time_12h = start_time
                
#                 # Find capacity
#                 cap = None
#                 for alloc in s.get("allocations", []):
#                     if str(alloc.get("productId")) == pid_str:
#                         cap = (
#                             alloc.get("bookableCapacityRemaining")
#                             or alloc.get("ticketCapacityRemaining")
#                         )
#                         break
                
#                 if cap is None:
#                     cap = s.get("ticketCapacityRemaining") or s.get("bookableCapacityRemaining")
                
#                 if isinstance(cap, (int, float)) and cap > 0:
#                     slots_24h.append(start_time_24h)
#                     slots_12h.append(start_time_12h)
#                     availability[start_time_24h] = int(cap)
        
#         return slots_24h, availability, slots_12h
    
#     def get(self, request):
#         """
#         Handle GET request for product availability
#         Expected parameters:
#         - date (required): YYYY-MM-DD
#         - client_id (required): Location ID (uses location_id from Location table)
#         - product_id (optional): Override location's default product_id
#         - category_name (optional): Override location's default category
#         - quantity (optional): Number of jumpers
#         - time (optional): Specific time slot (HH:MM format)
#         """
#         # Extract parameters
#         date = request.GET.get('date')
#         client_id = request.GET.get('client_id')  # This is location_id
#         product_id = request.GET.get('product_id')
#         category_name = request.GET.get('category_name')
#         quantity = request.GET.get('quantity')
#         time_str = request.GET.get('time')
        
#         # Validate required parameters
#         if not date:
#             return Response({
#                 "status": "error",
#                 "message": "Date parameter is required",
#                 "data": {"availability": "Unavailable"}
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         if not client_id:
#             return Response({
#                 "status": "error",
#                 "message": "client_id parameter is required (Location ID)",
#                 "data": {"availability": "Unavailable"}
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Parse date
#             date_obj = datetime.strptime(date, "%Y-%m-%d").date()
#         except ValueError:
#             return Response({
#                 "status": "error",
#                 "message": "Invalid date format. Use YYYY-MM-DD",
#                 "data": {"availability": "Unavailable"}
#             }, status=status.HTTP_400_BAD_REQUEST)
        
#         # Parse quantity if provided
#         if quantity:
#             try:
#                 quantity = int(quantity)
#                 if quantity <= 0:
#                     raise ValueError
#             except ValueError:
#                 return Response({
#                     "status": "error",
#                     "message": "Quantity must be a positive integer",
#                     "data": {"availability": "Unavailable"}
#                 }, status=status.HTTP_400_BAD_REQUEST)
        
#         try:
#             # Get location - ONLY USE THE SPECIFIED LOCATION ID
#             try:
#                 location = Location.objects.get(location_id=client_id)
#                 logger.info(f"Found location ID {client_id}: {location.location_name}")
#             except Location.DoesNotExist:
#                 logger.error(f"Location with ID {client_id} not found")
#                 return Response({
#                     "status": "error",
#                     "message": f"Location with ID {client_id} not found",
#                     "data": {"availability": "Unavailable"}
#                 }, status=status.HTTP_404_NOT_FOUND)
            
#             # CRITICAL FIX: Check if location has Roller credentials
#             # Don't fall back to any other location - strictly use only this location
#             if not location.roller_client_id or not location.roller_client_secret:
#                 logger.error(f"Location {location.location_name} (ID: {client_id}) does not have Roller API credentials configured")
#                 return Response({
#                     "status": "error",
#                     "message": f"Location {location.location_name} does not have Roller API credentials configured",
#                     "data": {"availability": "Unavailable"}
#                 }, status=status.HTTP_400_BAD_REQUEST)
            
#             # Get token - this will only use the specified location's credentials
#             api_token = self.get_roller_token(location)
#             if not api_token:
#                 logger.error(f"Failed to get API access token for location {location.location_name}")
#                 return Response({
#                     "status": "error",
#                     "message": f"Failed to get API access token for location {location.location_name}",
#                     "data": {"availability": "Unavailable"}
#                 }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
#             # Determine product_id to use
#             if product_id:
#                 try:
#                     current_product_id = int(product_id)
#                 except ValueError:
#                     return Response({
#                         "status": "error",
#                         "message": "Invalid product_id format",
#                         "data": {"availability": "Unavailable"}
#                     }, status=status.HTTP_400_BAD_REQUEST)
#             else:
#                 # Check if location has a default product_id
#                 # You might want to add a roller_product_id field to Location model
#                 # For now, we'll return an error if not provided
#                 return Response({
#                     "status": "error",
#                     "message": "product_id parameter is required",
#                     "data": {"availability": "Unavailable"}
#                 }, status=status.HTTP_400_BAD_REQUEST)
            
#             # Determine category to use
#             current_category = category_name if category_name else 'TESTB'
            
#             # Get all available slots (24-hour format and 12-hour format)
#             slots_24h, availability, slots_12h = self.get_available_slots(
#                 current_product_id, date_obj, current_category, api_token
#             )
            
#             # Create 12-hour format string for availability_slots
#             availability_slots_12h = ", ".join(slots_12h) if slots_12h else ""
            
#             # Check specific time
#             if time_str:
#                 # Parse and format the time to ensure consistent format
#                 try:
#                     time_obj = datetime.strptime(time_str, "%H:%M")
#                     time_formatted = time_obj.strftime("%H:%M")
#                 except ValueError:
#                     # If parsing fails, use as is
#                     time_formatted = time_str
                
#                 cap = availability.get(time_formatted)
                
#                 if cap is None:
#                     return Response({
#                         "status": "success",
#                         "message": f"Unavailable slot for {time_formatted}",
#                         "data": {
#                             "availability": "Unavailable",
#                             "availability_slots": availability_slots_12h,
#                             "depositPercentage": 50,
#                             "depositAmount": None
#                         }
#                     })
                
#                 # Check quantity
#                 if quantity and quantity > cap:
#                     return Response({
#                         "status": "success",
#                         "message": f"Insufficient capacity. Available: {cap}",
#                         "data": {
#                             "availability": "Unavailable",
#                             "availability_slots": availability_slots_12h,
#                             "depositPercentage": 50,
#                             "depositAmount": None
#                         }
#                     })
                
#                 # Convert specific time to 12-hour format for response
#                 try:
#                     time_12h = datetime.strptime(time_formatted, "%H:%M").strftime("%I:%M %p")
#                 except:
#                     time_12h = time_formatted
                
#                 return Response({
#                     "status": "success",
#                     "message": "success",
#                     "data": {
#                         "availability": time_12h,
#                         "availability_slots": availability_slots_12h,
#                         "depositPercentage": 50,
#                         "depositAmount": None,
#                         "capacity": cap
#                     }
#                 })
            
#             # No specific time requested - get all slots
            
#             # Filter by quantity if provided
#             if quantity:
#                 filtered_slots_24h = []
#                 filtered_slots_12h = []
                
#                 for slot_24h, slot_12h, cap in zip(slots_24h, slots_12h, [availability.get(slot) for slot in slots_24h]):
#                     if cap is not None and quantity <= cap:
#                         filtered_slots_24h.append(slot_24h)
#                         filtered_slots_12h.append(slot_12h)
                
#                 if not filtered_slots_24h:
#                     return Response({
#                         "status": "success",
#                         "message": "No available slots for requested quantity",
#                         "data": {
#                             "availability": "Unavailable",
#                             "availability_slots": availability_slots_12h,
#                             "depositPercentage": 50,
#                             "depositAmount": None
#                         }
#                     })
                
#                 return Response({
#                     "status": "success",
#                     "message": "success",
#                     "data": {
#                         "availability": ", ".join(filtered_slots_12h),
#                         "availability_slots": availability_slots_12h,
#                         "depositPercentage": 50,
#                         "depositAmount": None,
#                         "totalSlots": len(filtered_slots_12h)
#                     }
#                 })
            
#             # Return all slots without quantity filter
#             if not slots_24h:
#                 return Response({
#                     "status": "success",
#                     "message": "No available slots",
#                     "data": {
#                         "availability": "Unavailable",
#                         "availability_slots": "",
#                         "depositPercentage": 50,
#                         "depositAmount": None
#                     }
#                 })
            
#             return Response({
#                 "status": "success",
#                 "message": "success",
#                 "data": {
#                     "availability": ", ".join(slots_12h),  # 12-hour format for main availability
#                     "availability_slots": availability_slots_12h,  # Same as availability when no time specified
#                     "depositPercentage": 50,
#                     "depositAmount": None,
#                     "totalSlots": len(slots_12h)
#                 }
#             })
            
#         except Exception as e:
#             logger.exception(f"Unexpected error in availability check: {str(e)}")
#             return Response({
#                 "status": "error",
#                 "message": f"Internal server error: {str(e)}",
#                 "data": {"availability": "Unavailable"}
#             }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





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
                
                # Keep original 24-hour format
                start_time_24h = start_time
                
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
                    slots.append(start_time_24h)
                    availability[start_time_24h] = int(cap)
        
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
            
            # Get all available slots (in 24-hour format)
            slots, availability = self.get_available_slots(
                current_product_id, date_obj, current_category, api_token
            )
            
            # Create 24-hour format string for availability_slots
            availability_slots = ", ".join(slots) if slots else ""
            
            # Check specific time
            if time_str:
                # Parse and format the time to ensure consistent format (HH:MM)
                try:
                    time_obj = datetime.strptime(time_str, "%H:%M")
                    time_formatted = time_obj.strftime("%H:%M")
                except ValueError:
                    # If parsing fails, try to parse with AM/PM format
                    try:
                        time_obj = datetime.strptime(time_str, "%I:%M %p")
                        time_formatted = time_obj.strftime("%H:%M")
                    except:
                        # If all parsing fails, use as is
                        time_formatted = time_str
                
                cap = availability.get(time_formatted)
                
                if cap is None:
                    return Response({
                        "status": "success",
                        "message": f"Unavailable slot for {time_formatted}",
                        "data": {
                            "availability": "Unavailable",
                            "availability_slots": availability_slots,
                            "depositPercentage": 50,
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
                            "availability_slots": availability_slots,
                            "depositPercentage": 50,
                            "depositAmount": None
                        }
                    })
                
                return Response({
                    "status": "success",
                    "message": "success",
                    "data": {
                        "availability": time_formatted,
                        "availability_slots": availability_slots,
                        "depositPercentage": 50,
                        "depositAmount": None,
                        "capacity": cap
                    }
                })
            
            # No specific time requested - get all slots
            
            # Filter by quantity if provided
            if quantity:
                filtered_slots = []
                
                for slot, cap in availability.items():
                    if cap is not None and quantity <= cap:
                        filtered_slots.append(slot)
                
                if not filtered_slots:
                    return Response({
                        "status": "success",
                        "message": "No available slots for requested quantity",
                        "data": {
                            "availability": "Unavailable",
                            "availability_slots": availability_slots,
                            "depositPercentage": 50,
                            "depositAmount": None
                        }
                    })
                
                return Response({
                    "status": "success",
                    "message": "success",
                    "data": {
                        "availability": ", ".join(filtered_slots),
                        "availability_slots": availability_slots,
                        "depositPercentage": 50,
                        "depositAmount": None,
                        "totalSlots": len(filtered_slots)
                    }
                })
            
            # Return all slots without quantity filter
            if not slots:
                return Response({
                    "status": "success",
                    "message": "No available slots",
                    "data": {
                        "availability": "Unavailable",
                        "availability_slots": "",
                        "depositPercentage": 50,
                        "depositAmount": None
                    }
                })
            
            return Response({
                "status": "success",
                "message": "success",
                "data": {
                    "availability": ", ".join(slots),  # 24-hour format
                    "availability_slots": availability_slots,  # Same as availability when no time specified
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

