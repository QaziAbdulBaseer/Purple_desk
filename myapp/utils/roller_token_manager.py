# # utils/roller_token_manager.py
# import requests
# from django.utils import timezone
# import logging

# logger = logging.getLogger(__name__)

# def get_or_refresh_roller_token(location):
#     """
#     Get Roller token for a location.
#     If token exists and is not expired, return it.
#     If expired or doesn't exist, fetch new token and save it.
#     """
#     # Check if token exists and is not expired
#     if not location.is_token_expired() and location.roller_access_token:
#         return location.roller_access_token
    
#     # Check if we have credentials
#     if not location.roller_client_id or not location.roller_client_secret:
#         logger.warning(f"Location {location.location_name} has no Roller API credentials")
#         return None
    
#     # Fetch new token
#     url = "https://api.haveablast.roller.app/token"
#     payload = {
#         "client_id": location.roller_client_id,
#         "client_secret": location.roller_client_secret
#     }
#     headers = {
#         "Content-Type": "application/json",
#         "Accept": "application/json",
#     }
    
#     try:
#         response = requests.post(url, json=payload, headers=headers, timeout=30)
#         response.raise_for_status()
#         data = response.json()
#         access_token = data.get("access_token")
        
#         if access_token:
#             # Save token to location
#             location.roller_access_token = access_token
#             location.roller_token_created_at = timezone.now()
#             location.save(update_fields=['roller_access_token', 'roller_token_created_at'])
#             logger.info(f"New token obtained for location {location.location_name}")
#             return access_token
#         else:
#             logger.error(f"No access token in response for location {location.location_name}")
#             return None
            
#     except requests.exceptions.RequestException as e:
#         logger.error(f"Error getting token for location {location.location_name}: {str(e)}")
#         return None
#     except Exception as e:
#         logger.error(f"Error processing token response for location {location.location_name}: {str(e)}")
#         return None



# utils/roller_token_manager.py
import requests
from django.utils import timezone
import logging
from datetime import timedelta

logger = logging.getLogger(__name__)

def get_or_refresh_roller_token(location):
    """
    Get Roller token for a location.
    If token exists and is not expired, return it.
    If expired or doesn't exist, fetch new token and save it.
    """
    # Check if token exists and is not expired
    if location.roller_access_token and location.roller_token_created_at:
        # Calculate age of token
        token_age = timezone.now() - location.roller_token_created_at
        
        # If token is less than 22 hours old, use it (with 1 hour buffer)
        if token_age < timedelta(hours=22):
            logger.info(f"Using existing token for location {location.location_name} (age: {token_age})")
            return location.roller_access_token
    
    # Token is expired or doesn't exist - fetch new one
    logger.info(f"Token expired or not found for location {location.location_name}, fetching new token")
    
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
        
        if response.status_code == 200:
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
                logger.error(f"No access token in response for location {location.location_name}: {data}")
                return None
        else:
            logger.error(f"Error getting token for location {location.location_name}: {response.status_code} - {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        logger.error(f"Network error getting token for location {location.location_name}: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error processing token response for location {location.location_name}: {str(e)}")
        return None

