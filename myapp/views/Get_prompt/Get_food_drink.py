import pandas as pd
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any, Optional
from myapp.model.birthday_party_packages_model import BirthdayPartyPackage
from myapp.model.balloon_party_packages_model import BalloonPartyPackage
from myapp.model.items_food_drinks_model import ItemsFoodDrinks
from myapp.model.hours_of_operations_model import HoursOfOperation
from myapp.model.locations_model import Location
from asgiref.sync import sync_to_async
from django.db.models import Q


async def format_food_drinks_for_display(food_data: Dict, location_name: str) -> str:
    """Format the food and drinks data for easy reading - async version"""
    def _format_output():
        output_lines = []
        
        # Header
        output_lines.append("=== FOOD & DRINKS ITEMS INFORMATION ===")
        output_lines.append(f"Location: {location_name}")
        output_lines.append(f"Total Available Items: {food_data['total_items']}")
        output_lines.append(f"Categories: {', '.join(food_data['categories'])}")
        output_lines.append("")
        
        # Items by category
        for category in food_data["categories"]:
            output_lines.append(f"=== {category.upper()} ===")
            output_lines.append(f"Total Items in Category: {len(food_data['items_by_category'][category])}")
            output_lines.append(f"Popular Items: {len(food_data['popular_items_by_category'][category])}")
            output_lines.append(f"Other Items: {len(food_data['other_items_by_category'][category])}")
            output_lines.append("")
            
            # Popular items
            if food_data["popular_items_by_category"][category]:
                output_lines.append("Popular Items:")
                for item in food_data["popular_items_by_category"][category]:
                    price_str = f" | Price($):{item['price']}" if item['price'] else ""
                    output_lines.append(f"  - {item['item']}{price_str}")
            
            # Other items
            if food_data["other_items_by_category"][category]:
                output_lines.append("\nOther Items:")
                for item in food_data["other_items_by_category"][category]:
                    price_str = f" | Price($):{item['price']}" if item['price'] else ""
                    output_lines.append(f"  - {item['item']}{price_str}")
            
            output_lines.append("")
        
        return "\n".join(output_lines)
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _format_output)



async def food_drinks_info(food_data: Dict) -> Dict[str, str]:
    """
    Process food and drinks information and format it for the prompt
    """
    food_section_lines = []
    
    # Add header
    food_section_lines.append("####### Food and Drinks Options")
    
    # Process each category
    for category in food_data["categories"]:
        category_name = category.replace('_', ' ').title()
        
        # Check if this is Pizzas or Party tray for special formatting
        if 'pizza' in category.lower():
            food_section_lines.append(f"**{category_name}(Included In Birthday Party Package) options:**")
            food_section_lines.append(f"Here are the popular {category_name} options:")
        else:
            food_section_lines.append(f"**{category_name} options:**")
            food_section_lines.append(f"(These are available as add-ons:)Here are the popular {category_name} options:")
        
        # Add popular items
        popular_items = food_data["popular_items_by_category"][category]
        for item in popular_items:
            price_str = f" | Price($):{item['price']}" if item['price'] else ""
            additional_info = ""
            if item['additional_instructions']:
                additional_info = f" ({item['additional_instructions']})"
            food_section_lines.append(f"- {item['item']}{additional_info}{price_str}")
        
        # Add prompt for other items
        other_items = food_data["other_items_by_category"][category]
        if other_items:
            food_section_lines.append(f"Do you want to know about other {category_name} options? if user says 'yes' then tell below:")
            for item in other_items:
                price_str = f" | Price($):{item['price']}" if item['price'] else ""
                additional_info = ""
                if item['additional_instructions']:
                    additional_info = f" ({item['additional_instructions']})"
                food_section_lines.append(f"- {item['item']}{additional_info}{price_str}")
        
        food_section_lines.append("")
    
    # Add pricing logic
    food_section_lines.append("""
## PRICING LOGIC FOR FOOD
Standard Birthday Party Packages (Epic Birthday Party Package, Mega VIP Birthday Party Package, Little Leaper Birthday Party Package, Glow Birthday Party Package):
Included:
- Base package includes:
2 pizzas
2 drinks
for up to 10 jumpers
Additional Jumper Logic:
For every 5 additional jumpers beyond the first 10, you get:
1 extra pizza (free)
1 extra drink (free)
Examples:
- 12 jumpers → 2 pizzas + 2 drinks (purchase separately)
- 15 jumpers → 2 pizzas + 2 drinks (base) + 1 extra pizza + 1 drink (for 5 extra jumpers)
- 20 jumpers → 2 pizzas + 2 drinks (base) + 2 extra pizzas + 2 drinks (for 10 extra jumpers)
*Basic Birthday Party Package:*
- No food/drinks included - all purchased separately
*Party Trays:*
- Always additional purchases for any package
    """)
    
    return {
        "food_section": "\n".join(food_section_lines)
    }






async def get_structured_food_drinks_data(
    location_id: int,
    food_items: List[ItemsFoodDrinks]
) -> Dict[str, Any]:
    """
    Get structured food and drinks data for formatting
    """
    # Organize by category
    structured_data = {
        "total_items": len(food_items),
        "items_by_category": {},
        "categories": [],
        "popular_items_by_category": {},
        "other_items_by_category": {}
    }
    
    # Group items by category
    for item_obj in food_items:
        category = item_obj.category
        if category not in structured_data["categories"]:
            structured_data["categories"].append(category)
            structured_data["items_by_category"][category] = []
            structured_data["popular_items_by_category"][category] = []
            structured_data["other_items_by_category"][category] = []
        
        item_data = {
            "item": item_obj.item,
            "category": item_obj.category,
            "category_priority": item_obj.category_priority,
            "category_type": item_obj.category_type or "",
            "options_type_per_category": item_obj.options_type_per_category or "",
            "price": str(item_obj.price) if item_obj.price else "",
            "additional_instructions": item_obj.additional_instructions or "",
            "t_shirt_sizes": item_obj.t_shirt_sizes or "",
            "t_shirt_type": item_obj.t_shirt_type or "",
            "pitch_in_party_package": item_obj.pitch_in_party_package
        }
        
        structured_data["items_by_category"][category].append(item_data)
    
    # Split into popular and other items (first 2 are popular)
    for category, items in structured_data["items_by_category"].items():
        structured_data["popular_items_by_category"][category] = items[:2]
        structured_data["other_items_by_category"][category] = items[2:]
    
    return structured_data




async def get_food_drinks_info(location_id: int) -> Dict[str, Any]:
    """
    Main function to get formatted food and drinks information from database
    """
    
    @sync_to_async
    def get_food_items():
        return list(
            ItemsFoodDrinks.objects.filter(
                location_id=location_id
            ).select_related('location').order_by('category_priority', 'category', 'item')
        )
    
    @sync_to_async
    def get_location():
        return Location.objects.get(location_id=location_id)
    
    try:
        # Fetch data asynchronously
        food_items = await get_food_items()
        location = await get_location()
        
        # Convert to structured data
        structured_data = await get_structured_food_drinks_data(location_id, food_items)
        formatted_display = await format_food_drinks_for_display(structured_data, location.location_name)
        
        # Create the prompt sections
        food_info_dict = await food_drinks_info(structured_data)
        
        return {
            'structured_data': structured_data,
            'formatted_display': formatted_display,
            'food_info_dict': food_info_dict
        }
    except Exception as e:
        print(f"Error in get_food_drinks_info: {str(e)}")
        raise


