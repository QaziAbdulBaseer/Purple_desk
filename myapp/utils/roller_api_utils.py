# # utils/roller_api_utils.py
# import aiohttp
# import asyncio
# from datetime import datetime
# import json
# from django.utils import timezone
# from myapp.model.RollerAPICredentials_model import RollerAPICredentials
# from asgiref.sync import sync_to_async
# import logging
# from django.db import transaction

# logger = logging.getLogger(__name__)

# class RollerAPIError(Exception):
#     """Custom exception for Roller API errors"""
#     pass

# # Helper functions to run sync ORM operations in async context
# async def get_roller_credentials(location_id=None, category_name=None):
#     """Get roller credentials with sync_to_async"""
#     try:
#         if location_id and category_name:
#             return await sync_to_async(
#                 RollerAPICredentials.objects.get
#             )(location_id=location_id, category_name=category_name)
#         elif location_id:
#             return await sync_to_async(
#                 RollerAPICredentials.objects.get
#             )(location_id=location_id)
#         else:
#             return await sync_to_async(
#                 RollerAPICredentials.objects.first
#             )()
#     except RollerAPICredentials.DoesNotExist:
#         return None
#     except Exception as e:
#         logger.error(f"Error getting credentials: {str(e)}")
#         return None

# async def save_credentials_token(credentials, token):
#     """Save token to credentials with sync_to_async"""
#     try:
#         credentials.access_token = token
#         credentials.token_created_at = timezone.now()
        
#         # Use sync_to_async with atomic transaction
#         await sync_to_async(transaction.on_commit)(
#             lambda: credentials.save(update_fields=['access_token', 'token_created_at'])
#         )
#         return True
#     except Exception as e:
#         logger.error(f"Error saving token: {str(e)}")
#         return False

# async def get_roller_access_token(roller_credentials):
#     """
#     Get access token from Roller API, use stored token if valid
#     """
#     # Check if token exists and is not expired - sync check
#     is_expired = await sync_to_async(roller_credentials.is_token_expired)()
    
#     if not is_expired and roller_credentials.access_token:
#         logger.info(f"Using existing token for location {roller_credentials.location.name}")
#         return roller_credentials.access_token
    
#     logger.info(f"Fetching new token for location {roller_credentials.location.name}")
    
#     url = "https://api.haveablast.roller.app/token"
#     payload = {
#         "client_id": roller_credentials.client_id,
#         "client_secret": roller_credentials.client_secret
#     }
#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#     }
    
#     try:
#         async with aiohttp.ClientSession() as client_session:
#             async with client_session.post(url, json=payload, headers=headers) as res:
#                 if res.status != 200:
#                     error_text = await res.text()
#                     logger.error(f"Token request failed: {error_text}")
#                     raise RollerAPIError(f"Failed to get token: {error_text}")
                
#                 response = await res.json()
#                 access_token = response.get("access_token")
                
#                 if not access_token:
#                     raise RollerAPIError("No access token in response")
                
#                 # Update credentials in database
#                 await save_credentials_token(roller_credentials, access_token)
                
#                 logger.info(f"New token obtained for location {roller_credentials.location.name}")
#                 return access_token
                
#     except Exception as e:
#         logger.error(f"Error getting access token: {str(e)}")
#         raise RollerAPIError(f"Error getting access token: {str(e)}")

# async def get_product_availability(product_id, date, product_category, api_token):
#     """
#     Get product availability from Roller API
#     """
#     url = "https://api.haveablast.roller.app/product-availability"
#     headers = {
#         "Accept": "application/json",
#         "Authorization": f"Bearer {api_token}"
#     }
    
#     # Format date if it's a datetime object
#     if isinstance(date, datetime):
#         date_str = date.strftime("%Y-%m-%d")
#     else:
#         date_str = str(date)
    
#     params = {
#         "ProductIds": str(product_id),
#         "Date": date_str,
#         "ProductCategory": product_category,
#     }
    
#     try:
#         async with aiohttp.ClientSession() as client_session:
#             async with client_session.get(url, headers=headers, params=params) as res:
#                 if res.status != 200:
#                     error_text = await res.text()
#                     logger.error(f"Availability request failed: {error_text}")
#                     raise RollerAPIError(f"Failed to get availability: {error_text}")
                
#                 response = await res.json()
#                 return response
#     except Exception as e:
#         logger.error(f"Error getting product availability: {str(e)}")
#         raise RollerAPIError(f"Error getting product availability: {str(e)}")

# async def get_available_slots(product_id, date, product_category, api_token):
#     """
#     Get available slots and capacities for a product
#     """
#     resp = await get_product_availability(product_id, date, product_category, api_token)
    
#     # Ensure list
#     entries = resp if isinstance(resp, list) else resp.get("data") or [resp]
    
#     pid_str = str(product_id)
#     slots = []
#     availability = {}
    
#     for entry in entries:
#         if not isinstance(entry, dict):
#             continue
        
#         sessions = entry.get("sessions", [])
        
#         for s in sessions:
#             start_time = s.get("startTime")
#             if not start_time:
#                 continue
            
#             # Convert to AM/PM
#             try:
#                 start_time_ampm = datetime.strptime(start_time, "%H:%M").strftime("%I:%M %p")
#             except:
#                 start_time_ampm = start_time
            
#             # Find matching product allocation
#             cap = None
#             for alloc in s.get("allocations", []):
#                 if str(alloc.get("productId")) == pid_str:
#                     cap = (
#                         alloc.get("bookableCapacityRemaining")
#                         or alloc.get("ticketCapacityRemaining")
#                     )
#                     break
            
#             # Fallback to session-level capacity
#             if cap is None:
#                 cap = s.get("ticketCapacityRemaining") or s.get("bookableCapacityRemaining")
            
#             # Only include positive capacity
#             if isinstance(cap, (int, float)) and cap > 0:
#                 slots.append(start_time_ampm)
#                 availability[start_time_ampm] = int(cap)
    
#     return slots, availability

# async def check_single_time_availability(product_id, date, product_category, api_token, time_str, quantity=None):
#     """
#     Check availability for a specific time
#     """
#     slots, availability = await get_available_slots(product_id, date, product_category, api_token)
    
#     # Convert time to AM/PM format for matching
#     try:
#         time_obj = datetime.strptime(time_str, "%H:%M")
#         time_ampm = time_obj.strftime("%I:%M %p")
#     except:
#         time_ampm = time_str
    
#     cap = availability.get(time_ampm)
    
#     if cap is None:
#         return False, 0, "Time slot not available"
    
#     if quantity and quantity > cap:
#         return False, cap, f"Capacity exceeded. Available: {cap}"
    
#     return True, cap, f"Available capacity: {cap}"





import requests
import logging
from django.utils import timezone
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class RollerAPIUtils:
    def __init__(self, location):
        self.location = location
        self.base_url = "https://api.roller.app"
        self.token_url = "https://api.haveablast.roller.app/token"
    
    def get_access_token(self):
        """Get or refresh access token"""
        if not self.location.is_token_expired() and self.location.roller_access_token:
            return self.location.roller_access_token
        
        if not self.location.roller_client_id or not self.location.roller_client_secret:
            logger.error(f"Location {self.location.location_name} has no Roller API credentials")
            return None
        
        try:
            response = requests.post(
                self.token_url,
                json={
                    "client_id": self.location.roller_client_id,
                    "client_secret": self.location.roller_client_secret
                },
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                },
                timeout=30
            )
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")
            
            if access_token:
                self.location.roller_access_token = access_token
                self.location.roller_token_created_at = timezone.now()
                self.location.save(update_fields=['roller_access_token', 'roller_token_created_at'])
                logger.info(f"New token obtained for location {self.location.location_name}")
                return access_token
            else:
                logger.error(f"No access token in response for location {self.location.location_name}")
                return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting token for location {self.location.location_name}: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing token response for location {self.location.location_name}: {str(e)}")
            return None
    
    def create_draft_booking(self, booking_data):
        """
        Create draft booking in Roller system
        
        Args:
            booking_data: Dict containing booking information
        
        Returns:
            Dict with Roller API response or None if failed
        """
        access_token = self.get_access_token()
        if not access_token:
            logger.error("No access token available")
            return None
        
        try:
            # Generate external ID
            external_id = f"PD-{datetime.now().strftime('%Y%m%d%H%M%S')}-{self.location.location_id}"
            
            # Prepare the payload for Roller API
            roller_payload = {
                "externalId": external_id,
                "name": f"{booking_data['customer']['first_name']} {booking_data['customer']['last_name']}",
                "comments": booking_data.get('comments', ''),
                "companyId": booking_data.get('company_id', 12345),  # Default company ID or get from location
                "customer": {
                    "firstName": booking_data['customer']['first_name'],
                    "lastName": booking_data['customer']['last_name'],
                    "email": booking_data['customer']['email'],
                    "phone": booking_data['customer']['phone']
                },
                "items": [],
                "sendConfirmations": False
            }
            
            # Add items from products
            for product in booking_data.get('products', []):
                # Convert productId to integer if it's a string
                product_id = int(product['productId']) if isinstance(product['productId'], str) else product['productId']
                
                item = {
                    "productId": product_id,
                    "quantity": product['quantity'],
                    "bookingDate": booking_data['bookingDate'],
                    "startTime": product['startTime']
                }
                
                # Add priceOverride if available
                if product.get('priceOverride'):
                    item["priceOverride"] = product['priceOverride']
                
                # Add party package inclusions if inclusion is True
                if product.get('inclusion', False):
                    if 'partyPackageInclusions' not in item:
                        item["partyPackageInclusions"] = []
                    item["partyPackageInclusions"].append({
                        "productId": str(product['productId']),
                        "quantity": product['quantity']
                    })
                
                roller_payload["items"].append(item)
            
            logger.info(f"Sending draft booking request to Roller: {json.dumps(roller_payload, indent=2)}")
            
            # Make API call
            response = requests.post(
                f"{self.base_url}/bookings/draft",
                json=roller_payload,
                headers={
                    "Content-Type": "application/json",
                    "Accept": "application/json",
                    "Authorization": f"Bearer {access_token}"
                },
                timeout=30
            )
            
            logger.info(f"Roller API response status: {response.status_code}")
            
            if response.status_code != 200:
                logger.error(f"Roller API error: {response.status_code} - {response.text}")
                return None
            
            roller_response = response.json()
            logger.info(f"Draft booking created successfully: {roller_response.get('uniqueId')}")
            return roller_response
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error creating draft booking: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                logger.error(f"Response content: {e.response.text}")
        except Exception as e:
            logger.error(f"Unexpected error creating draft booking: {str(e)}")
        
        return None




async def roller_booking(payload):
    url = "https://api.haveablast.roller.app/bookings"
    api_token = get_or_refresh_roller_token(location)
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_token}"
    }

    print("This is the payload being sent to Roller API: " , payload)
    print(heloo)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            headers=headers,
            json=payload
        ) as res:
            return await res.json()

