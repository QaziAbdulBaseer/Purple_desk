

# # hi see that code. i want you update that code. 

# # I want its just give the food and drink data
# # and i want you have to show that on the base of the (Options Type  on base of primery and secondary etc)


# # this is the example of the prompt that i want you will return 


# # example prompt= == =

# ---
# ## *FOOD & DRINK GUIDELINES*
# ####### Food and Drinks Options
# **Pizzas(Included In Birthday Party Package) options:**
# Here are the popular Pizzas options:
# - cheese pizza (1 pizza serving for 5 jumpers) | Price($):20.0
# - pepperoni pizza (1 pizza serving for 5 jumpers) | Price($):22.0
# Do you want to know about other Pizzas options? if user says 'yes' then tell below:
# - sausage pizza (1 pizza serving for 5 jumpers) | Price($):22.0
# **Drinks(Included In Birthday Party Package) options:**
# Here are the popular Drinks options:
# - pitcher of pink lemonade (1 pitcher serving for 5 jumpers) | Price($):10.49
# - pitcher of starry (1 pitcher serving for 5 jumpers) | Price($):10.49
# - pitcher of diet pepsi (1 pitcher serving for 5 jumpers) | Price($):10.49
# - pitcher of pepsi (1 pitcher serving for 5 jumpers) | Price($):10.49
# Do you want to know about other Drinks options? if user says 'yes' then tell below:
# - pitcher of orange soda (1 pitcher serving for 5 jumpers) | Price($):10.49
# - pitcher of fruit punch (1 pitcher serving for 5 jumpers) | Price($):10.49
# - pitcher of lemonade (1 pitcher serving for 5 jumpers) | Price($):10.49
# - pitcher of wild cherry pepsi (1 pitcher serving for 5 jumpers) | Price($):nan
# **Party tray options:**
# (These are available as add-ons:)Here are the popular Party tray options:
# - chicken tender platter (nan) | Price($):32.0
# - french fry platter (nan) | Price($):16.0
# - mini churro platter (nan) | Price($):15.0
# Do you want to know about other Party tray options? if user says 'yes' then tell below:
# - pretzel nugget platter (nan) | Price($):20.0
# - popcorn chicken platter (nan) | Price($):40.0
# **Other Party Addon options (Donot Tell Until user mentions):**
# These add-ons are available (only mention if user explicitly asks):
# - icee bundle (10 cups) | Price($):40.0
# - mini melts bundle (10 cups) | Price($):30.0
# - icee bundle additional (single icee bundle) | Price($):4.0
# - mini melts bundle additional (single mini melts bundle) | Price($):3.0
# ---
# ## PRICING LOGIC FOR FOOD
# Standard Birthday Party Packages (Epic Birthday Party Package, Mega VIP Birthday Party Package, Little Leaper Birthday Party Package, Glow Birthday Party Package):
# Included:
# - Base package includes:
# 2 pizzas
# 2 drinks
# for up to 10 jumpers
# Additional Jumper Logic:
# For every 5 additional jumpers beyond the first 10, you get:
# 1 extra pizza (free)
# 1 extra drink (free)
# Examples:
# - 12 jumpers → 2 pizzas + 2 drinks (purchase separately)
# - 15 jumpers → 2 pizzas + 2 drinks (base) + 1 extra pizza + 1 drink (for 5 extra jumpers)
# - 20 jumpers → 2 pizzas + 2 drinks (base) + 2 extra pizzas + 2 drinks (for 10 extra jumpers)
# *Basic Birthday Party Package:*
# - No food/drinks included - all purchased separately
# *Party Trays:*
# - Always additional purchases for any package
# ---



# # and this is the current code. like update that code..



# import pandas as pd
# import re
# import asyncio
# from concurrent.futures import ThreadPoolExecutor
# from typing import Dict, List, Any, Optional
# from myapp.model.birthday_party_packages_model import BirthdayPartyPackage
# from myapp.model.balloon_party_packages_model import BalloonPartyPackage
# from myapp.model.items_food_drinks_model import ItemsFoodDrinks
# from myapp.model.hours_of_operations_model import HoursOfOperation
# from myapp.model.locations_model import Location
# from asgiref.sync import sync_to_async
# from django.db.models import Q


# async def format_food_drinks_for_display(food_data: Dict, location_name: str) -> str:
#     """Format the food and drinks data for easy reading - async version"""
#     def _format_output():
#         output_lines = []
        
#         # Header
#         output_lines.append("=== FOOD & DRINKS ITEMS INFORMATION ===")
#         output_lines.append(f"Location: {location_name}")
#         output_lines.append(f"Total Available Items: {food_data['total_items']}")
#         output_lines.append(f"Categories: {', '.join(food_data['categories'])}")
#         output_lines.append("")
        
#         # Items by category
#         for category in food_data["categories"]:
#             output_lines.append(f"=== {category.upper()} ===")
#             output_lines.append(f"Total Items in Category: {len(food_data['items_by_category'][category])}")
#             output_lines.append(f"Popular Items: {len(food_data['popular_items_by_category'][category])}")
#             output_lines.append(f"Other Items: {len(food_data['other_items_by_category'][category])}")
#             output_lines.append("")
            
#             # Popular items
#             if food_data["popular_items_by_category"][category]:
#                 output_lines.append("Popular Items:")
#                 for item in food_data["popular_items_by_category"][category]:
#                     price_str = f" | Price($):{item['price']}" if item['price'] else ""
#                     output_lines.append(f"  - {item['item']}{price_str}")
            
#             # Other items
#             if food_data["other_items_by_category"][category]:
#                 output_lines.append("\nOther Items:")
#                 for item in food_data["other_items_by_category"][category]:
#                     price_str = f" | Price($):{item['price']}" if item['price'] else ""
#                     output_lines.append(f"  - {item['item']}{price_str}")
            
#             output_lines.append("")
        
#         return "\n".join(output_lines)
    
#     loop = asyncio.get_event_loop()
#     with ThreadPoolExecutor() as executor:
#         return await loop.run_in_executor(executor, _format_output)



# async def food_drinks_info(food_data: Dict) -> Dict[str, str]:
#     """
#     Process food and drinks information and format it for the prompt
#     """
#     food_section_lines = []
    
#     # Add header
#     food_section_lines.append("## *FOOD & DRINK GUIDELINES*")
#     food_section_lines.append("####### Food and Drinks Options")
    
#     # Process each category
#     for category in food_data["categories"]:
#         # Clean category name
#         clean_category = category.strip()
        
#         # Check category type to determine formatting
#         category_type = None
#         if clean_category.lower() == "pizza":
#             category_type = "included"
#         elif clean_category.lower() == "drinks":
#             # Check if any drink items have 'included_in_package' type
#             for item in food_data["items_by_category"][category]:
#                 if item.get('category_type') == 'included_in_package':
#                     category_type = "included"
#                     break
        
#         # Format category header based on type
#         if category_type == "included":
#             food_section_lines.append(f"**{clean_category.title()}(Included In Birthday Party Package) options:**")
#             food_section_lines.append(f"Here are the popular {clean_category.title()} options:")
#         else:
#             food_section_lines.append(f"**{clean_category.title()} options:**")
#             # Only show "These are available as add-ons:" for non-included categories
#             if clean_category.lower() not in ['pizza', 'drinks']:
#                 food_section_lines.append(f"(These are available as add-ons:)Here are the popular {clean_category.title()} options:")
#             else:
#                 food_section_lines.append(f"Here are the popular {clean_category.title()} options:")
        
#         # Add popular items (first 2 items in category)
#         popular_items = food_data["popular_items_by_category"][category]
#         for item in popular_items:
#             # Format item name with additional instructions if present
#             item_name = item['item']
#             if item['additional_instructions'] and item['additional_instructions'].lower() != 'nan':
#                 item_name = f"{item['item']} ({item['additional_instructions']})"
            
#             # Format price - handle NaN values
#             price = item['price']
#             if price and price.lower() != 'nan' and price != 'None':
#                 price_str = f" | Price($):{price}"
#             else:
#                 price_str = ""
            
#             food_section_lines.append(f"- {item_name}{price_str}")
        
#         # Add prompt for other items if they exist
#         other_items = food_data["other_items_by_category"][category]
#         if other_items:
#             food_section_lines.append(f"Do you want to know about other {clean_category.title()} options? if user says 'yes' then tell below:")
#             for item in other_items:
#                 # Format item name with additional instructions if present
#                 item_name = item['item']
#                 if item['additional_instructions'] and item['additional_instructions'].lower() != 'nan':
#                     item_name = f"{item['item']} ({item['additional_instructions']})"
                
#                 # Format price - handle NaN values
#                 price = item['price']
#                 if price and price.lower() != 'nan' and price != 'None':
#                     price_str = f" | Price($):{price}"
#                 else:
#                     price_str = ""
                
#                 food_section_lines.append(f"- {item_name}{price_str}")
        
#         food_section_lines.append("")
    
#     # Add pricing logic
#     food_section_lines.append("---")
#     food_section_lines.append("## PRICING LOGIC FOR FOOD")
#     food_section_lines.append("Standard Birthday Party Packages (Epic Birthday Party Package, Mega VIP Birthday Party Package, Little Leaper Birthday Party Package, Glow Birthday Party Package):")
#     food_section_lines.append("Included:")
#     food_section_lines.append("- Base package includes:")
#     food_section_lines.append("2 pizzas")
#     food_section_lines.append("2 drinks")
#     food_section_lines.append("for up to 10 jumpers")
#     food_section_lines.append("Additional Jumper Logic:")
#     food_section_lines.append("For every 5 additional jumpers beyond the first 10, you get:")
#     food_section_lines.append("1 extra pizza (free)")
#     food_section_lines.append("1 extra drink (free)")
#     food_section_lines.append("Examples:")
#     food_section_lines.append("- 12 jumpers → 2 pizzas + 2 drinks (purchase separately)")
#     food_section_lines.append("- 15 jumpers → 2 pizzas + 2 drinks (base) + 1 extra pizza + 1 drink (for 5 extra jumpers)")
#     food_section_lines.append("- 20 jumpers → 2 pizzas + 2 drinks (base) + 2 extra pizzas + 2 drinks (for 10 extra jumpers)")
#     food_section_lines.append("*Basic Birthday Party Package:*")
#     food_section_lines.append("- No food/drinks included - all purchased separately")
#     food_section_lines.append("*Party Trays:*")
#     food_section_lines.append("- Always additional purchases for any package")
#     food_section_lines.append("---")
    
#     return {
#         "food_section": "\n".join(food_section_lines)
#     }






# async def get_structured_food_drinks_data(
#     location_id: int,
#     food_items: List[ItemsFoodDrinks]
# ) -> Dict[str, Any]:
#     """
#     Get structured food and drinks data for formatting
#     """
#     # Organize by category (case-insensitive grouping)
#     structured_data = {
#         "total_items": len(food_items),
#         "items_by_category": {},
#         "categories": [],
#         "popular_items_by_category": {},
#         "other_items_by_category": {}
#     }
    
#     # First, normalize category names and group them
#     category_mapping = {}
#     for item_obj in food_items:
#         original_category = item_obj.category
#         # Normalize category name (strip, lower case, then capitalize first letter of each word)
#         normalized_category = ' '.join(word.capitalize() for word in original_category.strip().lower().split())
        
#         if normalized_category not in category_mapping:
#             category_mapping[normalized_category] = []
        
#         item_data = {
#             "item": item_obj.item,
#             "original_category": original_category,
#             "category": normalized_category,
#             "category_priority": item_obj.category_priority,
#             "category_type": item_obj.category_type or "",
#             "options_type_per_category": item_obj.options_type_per_category or "",
#             "price": str(item_obj.price) if item_obj.price else "",
#             "additional_instructions": item_obj.additional_instructions or "",
#             "t_shirt_sizes": item_obj.t_shirt_sizes or "",
#             "t_shirt_type": item_obj.t_shirt_type or "",
#             "pitch_in_party_package": item_obj.pitch_in_party_package
#         }
        
#         category_mapping[normalized_category].append(item_data)
    
#     # Now sort categories by priority and name
#     for normalized_category, items in category_mapping.items():
#         # Sort items within each category by options_type_per_category (primary first) then by item name
#         sorted_items = sorted(items, key=lambda x: (
#             x['options_type_per_category'] != 'primary',  # Primary items first
#             x['item'].lower()
#         ))
        
#         structured_data["items_by_category"][normalized_category] = sorted_items
#         structured_data["categories"].append(normalized_category)
    
#     # Sort categories by priority (lowest first) and then by name
#     def get_category_priority(category_name):
#         # Find the highest priority (lowest number) in the category
#         items = structured_data["items_by_category"][category_name]
#         if items:
#             return min(item['category_priority'] for item in items)
#         return 999
    
#     structured_data["categories"] = sorted(
#         structured_data["categories"],
#         key=lambda cat: (get_category_priority(cat), cat.lower())
#     )
    
#     # Split into popular and other items (first 2 are popular)
#     for category, items in structured_data["items_by_category"].items():
#         # For Pizza and Drinks, show 2 popular items; for others, show all as popular
#         if category.lower() in ['pizza', 'drinks']:
#             structured_data["popular_items_by_category"][category] = items[:2]
#             structured_data["other_items_by_category"][category] = items[2:]
#         else:
#             # For other categories (Merchandise, Party Tray), show all as popular
#             structured_data["popular_items_by_category"][category] = items
#             structured_data["other_items_by_category"][category] = []
    
#     return structured_data




# async def get_food_drinks_info(location_id: int) -> Dict[str, Any]:
#     """
#     Main function to get formatted food and drinks information from database
#     """
    
#     @sync_to_async
#     def get_food_items():
#         return list(
#             ItemsFoodDrinks.objects.filter(
#                 location_id=location_id
#             ).select_related('location').order_by('category_priority', 'category', 'item')
#         )
    
#     @sync_to_async
#     def get_location():
#         return Location.objects.get(location_id=location_id)
    
#     try:
#         # Fetch data asynchronously
#         food_items = await get_food_items()
#         location = await get_location()
        
#         # Convert to structured data
#         structured_data = await get_structured_food_drinks_data(location_id, food_items)
#         formatted_display = await format_food_drinks_for_display(structured_data, location.location_name)
        
#         # Create the prompt sections
#         food_info_dict = await food_drinks_info(structured_data)
        
#         return {
#             'structured_data': structured_data,
#             'formatted_display': formatted_display,
#             'food_info_dict': food_info_dict
#         }
#     except Exception as e:
#         print(f"Error in get_food_drinks_info: {str(e)}")
#         raise




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
        output_lines.append("")
        
        # Items by category
        for category_info in food_data["categories"]:
            category = category_info["name"]
            category_type = category_info["type"]
            
            output_lines.append(f"=== {category.upper()} ===")
            output_lines.append(f"Category Type: {category_type}")
            output_lines.append(f"Total Items: {len(food_data['items_by_category'][category])}")
            
            # Primary items
            if food_data["primary_items_by_category"][category]:
                output_lines.append("\nPrimary Items:")
                for item in food_data["primary_items_by_category"][category]:
                    price_str = f" | Price($):{item['price']}" if item['price'] and item['price'].lower() != 'nan' else ""
                    instructions = f" ({item['additional_instructions']})" if item['additional_instructions'] and item['additional_instructions'].lower() != 'nan' else ""
                    output_lines.append(f"  - {item['item']}{instructions}{price_str}")
            
            # Secondary items
            if food_data["secondary_items_by_category"][category]:
                output_lines.append("\nSecondary Items:")
                for item in food_data["secondary_items_by_category"][category]:
                    price_str = f" | Price($):{item['price']}" if item['price'] and item['price'].lower() != 'nan' else ""
                    instructions = f" ({item['additional_instructions']})" if item['additional_instructions'] and item['additional_instructions'].lower() != 'nan' else ""
                    output_lines.append(f"  - {item['item']}{instructions}{price_str}")
            
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
    food_section_lines.append("---")
    food_section_lines.append("## *FOOD & DRINK GUIDELINES*")
    food_section_lines.append("####### Food and Drinks Options")
    
    # Define category order and display names based on your example
    category_order = ["Pizza", "Drinks", "Party Tray", "Other Party Addon"]
    category_display_names = {
        "Pizza": "Pizzas",
        "Drinks": "Drinks",
        "Party Tray": "Party tray options",
        "Other Party Addon": "Other Party Addon options"
    }
    
    # Process categories in specific order
    for category in category_order:
        if category not in food_data["items_by_category"]:
            continue
            
        display_name = category_display_names.get(category, category)
        items = food_data["items_by_category"][category]
        
        # Check if category is included in package
        is_included = False
        for item in items:
            if item.get('category_type') == 'included_in_package':
                is_included = True
                break
        
        # Format category header
        if is_included:
            food_section_lines.append(f"**{display_name}(Included In Birthday Party Package) options:**")
        else:
            if category == "Other Party Addon":
                food_section_lines.append(f"**{display_name} (Donot Tell Until user mentions):**")
                food_section_lines.append("These add-ons are available (only mention if user explicitly asks):")
                # For Other Party Addon, show all items without splitting
                for item in items:
                    item_name = item['item']
                    if item['additional_instructions'] and item['additional_instructions'].lower() != 'nan':
                        item_name = f"{item['item']} ({item['additional_instructions']})"
                    
                    price = item['price']
                    if price and price.lower() != 'nan' and price != 'None':
                        price_str = f" | Price($):{price}"
                    else:
                        price_str = ""
                    
                    food_section_lines.append(f"- {item_name}{price_str}")
                food_section_lines.append("")
                continue
            else:
                food_section_lines.append(f"**{display_name}:**")
                if category == "Party Tray":
                    food_section_lines.append(f"(These are available as add-ons:)Here are the popular {display_name}:")
                else:
                    food_section_lines.append(f"Here are the popular {display_name} options:")
        
        # Get primary items (popular items)
        primary_items = food_data["primary_items_by_category"].get(category, [])
        secondary_items = food_data["secondary_items_by_category"].get(category, [])
        
        # Show primary items (popular items)
        for item in primary_items:
            item_name = item['item']
            if item['additional_instructions'] and item['additional_instructions'].lower() != 'nan':
                item_name = f"{item['item']} ({item['additional_instructions']})"
            
            price = item['price']
            if price and price.lower() != 'nan' and price != 'None':
                price_str = f" | Price($):{price}"
            else:
                price_str = ""
            
            food_section_lines.append(f"- {item_name}{price_str}")
        
        # Show secondary items if they exist
        if secondary_items:
            food_section_lines.append(f"Do you want to know about other {display_name}? if user says 'yes' then tell below:")
            for item in secondary_items:
                item_name = item['item']
                if item['additional_instructions'] and item['additional_instructions'].lower() != 'nan':
                    item_name = f"{item['item']} ({item['additional_instructions']})"
                
                price = item['price']
                if price and price.lower() != 'nan' and price != 'None':
                    price_str = f" | Price($):{price}"
                else:
                    price_str = ""
                
                food_section_lines.append(f"- {item_name}{price_str}")
        
        food_section_lines.append("")
    
    # Add pricing logic
    food_section_lines.append("---")
    food_section_lines.append("## PRICING LOGIC FOR FOOD")
    food_section_lines.append("Standard Birthday Party Packages (Epic Birthday Party Package, Mega VIP Birthday Party Package, Little Leaper Birthday Party Package, Glow Birthday Party Package):")
    food_section_lines.append("Included:")
    food_section_lines.append("- Base package includes:")
    food_section_lines.append("2 pizzas")
    food_section_lines.append("2 drinks")
    food_section_lines.append("for up to 10 jumpers")
    food_section_lines.append("Additional Jumper Logic:")
    food_section_lines.append("For every 5 additional jumpers beyond the first 10, you get:")
    food_section_lines.append("1 extra pizza (free)")
    food_section_lines.append("1 extra drink (free)")
    food_section_lines.append("Examples:")
    food_section_lines.append("- 12 jumpers → 2 pizzas + 2 drinks (purchase separately)")
    food_section_lines.append("- 15 jumpers → 2 pizzas + 2 drinks (base) + 1 extra pizza + 1 drink (for 5 extra jumpers)")
    food_section_lines.append("- 20 jumpers → 2 pizzas + 2 drinks (base) + 2 extra pizzas + 2 drinks (for 10 extra jumpers)")
    food_section_lines.append("*Basic Birthday Party Package:*")
    food_section_lines.append("- No food/drinks included - all purchased separately")
    food_section_lines.append("*Party Trays:*")
    food_section_lines.append("- Always additional purchases for any package")
    food_section_lines.append("---")
    
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
    # Organize by category (case-insensitive grouping)
    structured_data = {
        "total_items": len(food_items),
        "items_by_category": {},
        "categories": [],
        "primary_items_by_category": {},
        "secondary_items_by_category": {}
    }
    
    # First, normalize category names and group them
    category_mapping = {}
    for item_obj in food_items:
        original_category = item_obj.category
        # Normalize category name (strip, lower case, then capitalize first letter of each word)
        normalized_category = ' '.join(word.capitalize() for word in original_category.strip().lower().split())
        
        if normalized_category not in category_mapping:
            category_mapping[normalized_category] = []
        
        item_data = {
            "item": item_obj.item,
            "original_category": original_category,
            "category": normalized_category,
            "category_priority": item_obj.category_priority,
            "category_type": item_obj.category_type or "",
            "options_type_per_category": item_obj.options_type_per_category or "",
            "price": str(item_obj.price) if item_obj.price else "",
            "additional_instructions": item_obj.additional_instructions or "",
            "t_shirt_sizes": item_obj.t_shirt_sizes or "",
            "t_shirt_type": item_obj.t_shirt_type or "",
            "pitch_in_party_package": item_obj.pitch_in_party_package
        }
        
        category_mapping[normalized_category].append(item_data)
    
    # Now sort categories by priority and name
    for normalized_category, items in category_mapping.items():
        # Sort items within each category by options_type_per_category (primary first) then by item name
        sorted_items = sorted(items, key=lambda x: (
            x['options_type_per_category'] != 'primary',  # Primary items first (True for non-primary, False for primary)
            x['item'].lower()
        ))
        
        structured_data["items_by_category"][normalized_category] = sorted_items
        
        # Store category with its type
        category_type = "unknown"
        if items:
            # Determine category type from first item or check if any item is included
            if any(item.get('category_type') == 'included_in_package' for item in items):
                category_type = "included"
            else:
                category_type = "addon"
        
        structured_data["categories"].append({
            "name": normalized_category,
            "type": category_type
        })
    
    # Sort categories by priority (lowest first) and then by name
    def get_category_priority(category_name):
        # Find the highest priority (lowest number) in the category
        items = structured_data["items_by_category"][category_name]
        if items:
            return min(item['category_priority'] for item in items)
        return 999
    
    structured_data["categories"] = sorted(
        structured_data["categories"],
        key=lambda cat: (get_category_priority(cat["name"]), cat["name"].lower())
    )
    
    # Split into primary and secondary items based on options_type_per_category
    for category, items in structured_data["items_by_category"].items():
        primary_items = []
        secondary_items = []
        
        for item in items:
            if item['options_type_per_category'].lower() == 'primary':
                primary_items.append(item)
            else:
                secondary_items.append(item)
        
        # If no items are marked as primary, use first few as primary based on category
        if not primary_items and items:
            if category.lower() in ['pizza', 'drinks']:
                primary_items = items[:2]  # First 2 items for pizza and drinks
                secondary_items = items[2:]
            elif category.lower() == 'party tray':
                primary_items = items[:3]  # First 3 items for party tray
                secondary_items = items[3:]
            else:
                # For other categories, all are primary
                primary_items = items
                secondary_items = []
        
        structured_data["primary_items_by_category"][category] = primary_items
        structured_data["secondary_items_by_category"][category] = secondary_items
    
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


