

import pandas as pd
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from myapp.model.jump_passes_model import JumpPass
from myapp.model.hours_of_operations_model import HoursOfOperation
from myapp.model.items_food_drinks_model import ItemsFoodDrinks
from myapp.model.locations_model import Location
from asgiref.sync import sync_to_async
import json


async def create_location_info_prompt(location_id: int) -> Dict[str, str]:
    """
    Create a dynamic location information prompt with location details and available items
    """
    
    @sync_to_async
    def get_location_details():
        return Location.objects.get(location_id=location_id)
    
    @sync_to_async
    def get_merchandise_items():
        return list(
            ItemsFoodDrinks.objects.filter(
                location_id=location_id,
                category__iexact='merchandise'
            ).select_related('location').order_by('item')
        )
    
    try:
        # Fetch data asynchronously
        location = await get_location_details()
        merchandise_items = await get_merchandise_items()
        
        # Create location information section
        location_lines = []
        location_lines.append("## Location")
        location_lines.append(f"### Step 1: Primary Location Response")
        location_lines.append(f"- When a user asks about {location.location_name}'s location, provide this information:")
        location_lines.append(f"- **Address**: {location.location_name} is located at {location.location_address}")
        
        if location.location_call_number:
            location_lines.append(f"- **Phone Number**: {location.location_call_number}")
        
        location_lines.append(f"- If directions are requested, **Say Exactly**: \"you can use google map to find {location.location_name.lower()}\"")
        
        location_lines.append(f"### Step 2: Follow-up Direction Requests")
        location_lines.append(f"Step: 2.1:")
        location_lines.append(f"Say exactly: \"To help your query on the direction I will connect you to our team member.\"")
        location_lines.append(f"Step: 2.2:")
        location_lines.append(f"*Use function: transfer_call_to_agent()*")
        location_lines.append(f"- transfer_reason: \"The user is requesting directions to the location.\"")
        
        location_lines.append(f"### Step 3: Visit Planning Inquiry")
        location_lines.append(f"- **After providing location information, if the customer has not previously mentioned a specific visiting day or date**:")
        location_lines.append(f"- **Ask exactly**: \"Are you planning to visit us today or another day?\"")
        
        location_lines.append(f"## Important Execution Notes:")
        location_lines.append(f"- Only proceed to the agent connection response if the user persists with direction questions after the initial location and google maps guidance")
        location_lines.append(f"- The visit planning question should only be asked once per conversation and only if no specific date/date was mentioned earlier")
        location_lines.append(f"- Use the exact phrases provided for consistency")
        
        # Create merchandise items section
        if merchandise_items:
            merchandise_lines = []
            merchandise_lines.append("## Other Items Pricing Information")
            merchandise_lines.append("### Available Items and Prices")
            
            for item in merchandise_items:
                # Format price with "point" for decimal
                price_str = ""
                if item.price:
                    # Convert decimal to string and replace decimal point with "point"
                    price_parts = str(item.price).split('.')
                    if len(price_parts) == 2:
                        dollars = price_parts[0]
                        cents = price_parts[1].rstrip('0') if price_parts[1] != '00' else '0'
                        if cents == '0':
                            price_str = f"${dollars} point 0"
                        else:
                            # Ensure two digits for cents
                            cents = cents[:2].ljust(2, '0')
                            price_str = f"${dollars} point {cents}"
                    else:
                        price_str = f"${price_parts[0]} point 0"
                
                item_name = item.item.lower()
                merchandise_lines.append(f"- {item_name}: {price_str}.")
            
            merchandise_section = "\n".join(merchandise_lines)
        else:
            merchandise_section = "## Other Items Pricing Information\n### Available Items and Prices\n- No merchandise items available at this location."
        
        # Combine sections
        location_section = "\n".join(location_lines)
        complete_prompt = f"{location_section}\n\n{merchandise_section}"
        
        return {
            "location_prompt": complete_prompt,
            "location_details": {
                "name": location.location_name,
                "address": location.location_address,
                "phone": location.location_call_number,
                "google_map_link": location.location_google_map_link
            },
            "merchandise_items": [
                {
                    "item": item.item,
                    "price": str(item.price) if item.price else None
                }
                for item in merchandise_items
            ]
        }
        
    except Exception as e:
        print(f"Error in create_location_info_prompt: {str(e)}")
        raise
    """
    Create a dynamic location information prompt with location details and available items
    """
    
    @sync_to_async
    def get_location_details():
        return Location.objects.get(location_id=location_id)
    
    @sync_to_async
    def get_merchandise_items():
        return list(
            ItemsFoodDrinks.objects.filter(
                location_id=location_id,
                category__iexact='merchandise'
            ).select_related('location').order_by('item')
        )
    
    try:
        # Fetch data asynchronously
        location = await get_location_details()
        merchandise_items = await get_merchandise_items()
        
        # Create location information section
        location_lines = []
        location_lines.append("## Location")
        location_lines.append(f"### Step 1: Primary Location Response")
        location_lines.append(f"- When a user asks about {location.location_name}'s location, provide this information:")
        location_lines.append(f"- **Address**: {location.location_name} is located at {location.location_address}")
        
        if location.location_call_number:
            location_lines.append(f"- **Phone Number**: {location.location_call_number}")
        
        location_lines.append(f"- If directions are requested, **Say Exactly**: \"you can use google map to find {location.location_name.lower()}\"")
        
        location_lines.append(f"### Step 2: Follow-up Direction Requests")
        location_lines.append(f"Step: 2.1:")
        location_lines.append(f"Say exactly: \"To help your query on the direction I will connect you to our team member.\"")
        location_lines.append(f"Step: 2.2:")
        location_lines.append(f"*Use function: transfer_call_to_agent()*")
        location_lines.append(f"- transfer_reason: \"The user is requesting directions to the location.\"")
        
        location_lines.append(f"### Step 3: Visit Planning Inquiry")
        location_lines.append(f"- **After providing location information, if the customer has not previously mentioned a specific visiting day or date**:")
        location_lines.append(f"- **Ask exactly**: \"Are you planning to visit us today or another day?\"")
        
        location_lines.append(f"## Important Execution Notes:")
        location_lines.append(f"- Only proceed to the agent connection response if the user persists with direction questions after the initial location and google maps guidance")
        location_lines.append(f"- The visit planning question should only be asked once per conversation and only if no specific date/date was mentioned earlier")
        location_lines.append(f"- Use the exact phrases provided for consistency")
        
        # Create merchandise items section
        if merchandise_items:
            merchandise_lines = []
            merchandise_lines.append("## Other Items Pricing Information")
            merchandise_lines.append("### Available Items and Prices")
            
            for item in merchandise_items:
                # Format price with "point" for decimal
                price_str = ""
                if item.price:
                    # Convert decimal to string and replace decimal point with "point"
                    price_parts = str(item.price).split('.')
                    if len(price_parts) == 2:
                        dollars = price_parts[0]
                        cents = price_parts[1].rstrip('0') if price_parts[1] != '00' else '0'
                        if cents == '0':
                            price_str = f"${dollars} point 0"
                        else:
                            # Ensure two digits for cents
                            cents = cents[:2].ljust(2, '0')
                            price_str = f"${dollars} point {cents}"
                    else:
                        price_str = f"${price_parts[0]} point 0"
                
                item_name = item.item.lower()
                merchandise_lines.append(f"- {item_name}: {price_str}.")
            
            merchandise_section = "\n".join(merchandise_lines)
        else:
            merchandise_section = "## Other Items Pricing Information\n### Available Items and Prices\n- No merchandise items available at this location."
        
        # Combine sections
        location_section = "\n".join(location_lines)
        complete_prompt = f"{location_section}\n\n{merchandise_section}"
        
        return {
            "location_prompt": complete_prompt,
            "location_details": {
                "name": location.location_name,
                "address": location.location_address,
                "phone": location.location_call_number,
                "google_map_link": location.location_google_map_link
            },
            "merchandise_items": [
                {
                    "item": item.item,
                    "price": str(item.price) if item.price else None
                }
                for item in merchandise_items
            ]
        }
        
    except Exception as e:
        print(f"Error in create_location_info_prompt: {str(e)}")
        raise


