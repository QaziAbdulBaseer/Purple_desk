# utils/roller_sync_helper.py
import aiohttp
import asyncio
from datetime import datetime
from django.utils import timezone
from myapp.model.RollerAPICredentials_model import RollerAPICredentials
import logging

logger = logging.getLogger(__name__)

class RollerSyncHelper:
    """
    Synchronous helper class that runs async code in a separate event loop
    """
    
    @staticmethod
    def get_roller_credentials_sync(location_id=None, category_name=None):
        """Synchronous method to get roller credentials"""
        try:
            if location_id and category_name:
                return RollerAPICredentials.objects.get(
                    location_id=location_id, 
                    category_name=category_name
                )
            elif location_id:
                return RollerAPICredentials.objects.get(location_id=location_id)
            else:
                return RollerAPICredentials.objects.first()
        except RollerAPICredentials.DoesNotExist:
            return None
        except Exception as e:
            logger.error(f"Error getting credentials: {str(e)}")
            return None
    
    @staticmethod
    def get_token_sync(roller_credentials):
        """Synchronous method to get token (runs async code in sync context)"""
        
        async def _get_token_async():
            from myapp.utils.roller_api_utils import get_roller_access_token
            return await get_roller_access_token(roller_credentials)
        
        # Run async function in sync context
        try:
            return asyncio.run(_get_token_async())
        except Exception as e:
            logger.error(f"Error getting token synchronously: {str(e)}")
            return None
    
    @staticmethod
    def get_availability_sync(product_id, date, category_name, api_token):
        """Synchronous method to get availability"""
        
        async def _get_availability_async():
            from myapp.utils.roller_api_utils import get_product_availability
            return await get_product_availability(product_id, date, category_name, api_token)
        
        try:
            return asyncio.run(_get_availability_async())
        except Exception as e:
            logger.error(f"Error getting availability: {str(e)}")
            return None
    
    @staticmethod
    def get_slots_sync(product_id, date, category_name, api_token):
        """Synchronous method to get slots"""
        
        async def _get_slots_async():
            from myapp.utils.roller_api_utils import get_available_slots
            return await get_available_slots(product_id, date, category_name, api_token)
        
        try:
            return asyncio.run(_get_slots_async())
        except Exception as e:
            logger.error(f"Error getting slots: {str(e)}")
            return [], {}
    
    @staticmethod
    def check_time_availability_sync(product_id, date, category_name, api_token, time_str, quantity=None):
        """Synchronous method to check time availability"""
        
        async def _check_time_async():
            from myapp.utils.roller_api_utils import check_single_time_availability
            return await check_single_time_availability(
                product_id, date, category_name, api_token, time_str, quantity
            )
        
        try:
            return asyncio.run(_check_time_async())
        except Exception as e:
            logger.error(f"Error checking time availability: {str(e)}")
            return False, 0, str(e)



