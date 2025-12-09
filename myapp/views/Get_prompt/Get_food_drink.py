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



# # async def food_drinks_info(food_data: Dict) -> Dict[str, str]:
# #     """
# #     Process food and drinks information and format it for the prompt
# #     """
# #     food_section_lines = []
    
# #     # Add header
# #     food_section_lines.append("####### Food and Drinks Options")
    
# #     # Process each category
# #     for category in food_data["categories"]:
# #         category_name = category.replace('_', ' ').title()
        
# #         # Check if this is Pizzas or Party tray for special formatting
# #         if 'pizza' in category.lower():
# #             food_section_lines.append(f"**{category_name}(Included In Birthday Party Package) options:**")
# #             food_section_lines.append(f"Here are the popular {category_name} options:")
# #         else:
# #             food_section_lines.append(f"**{category_name} options:**")
# #             food_section_lines.append(f"(These are available as add-ons:)Here are the popular {category_name} options:")
        
# #         # Add popular items
# #         popular_items = food_data["popular_items_by_category"][category]
# #         for item in popular_items:
# #             price_str = f" | Price($):{item['price']}" if item['price'] else ""
# #             additional_info = ""
# #             if item['additional_instructions']:
# #                 additional_info = f" ({item['additional_instructions']})"
# #             food_section_lines.append(f"- {item['item']}{additional_info}{price_str}")
        
# #         # Add prompt for other items
# #         other_items = food_data["other_items_by_category"][category]
# #         if other_items:
# #             food_section_lines.append(f"Do you want to know about other {category_name} options? if user says 'yes' then tell below:")
# #             for item in other_items:
# #                 price_str = f" | Price($):{item['price']}" if item['price'] else ""
# #                 additional_info = ""
# #                 if item['additional_instructions']:
# #                     additional_info = f" ({item['additional_instructions']})"
# #                 food_section_lines.append(f"- {item['item']}{additional_info}{price_str}")
        
# #         food_section_lines.append("")
    
# #     # Add pricing logic
# #     food_section_lines.append("""
# # ## PRICING LOGIC FOR FOOD
# # Standard Birthday Party Packages (Epic Birthday Party Package, Mega VIP Birthday Party Package, Little Leaper Birthday Party Package, Glow Birthday Party Package):
# # Included:
# # - Base package includes:
# # 2 pizzas
# # 2 drinks
# # for up to 10 jumpers
# # Additional Jumper Logic:
# # For every 5 additional jumpers beyond the first 10, you get:
# # 1 extra pizza (free)
# # 1 extra drink (free)
# # Examples:
# # - 12 jumpers → 2 pizzas + 2 drinks (purchase separately)
# # - 15 jumpers → 2 pizzas + 2 drinks (base) + 1 extra pizza + 1 drink (for 5 extra jumpers)
# # - 20 jumpers → 2 pizzas + 2 drinks (base) + 2 extra pizzas + 2 drinks (for 10 extra jumpers)
# # *Basic Birthday Party Package:*
# # - No food/drinks included - all purchased separately
# # *Party Trays:*
# # - Always additional purchases for any package
# #     """)
    
# #     return {
# #         "food_section": "\n".join(food_section_lines)
# #     }



# async def food_drinks_info(food_data: Dict) -> Dict[str, str]:
#     """
#     Process food and drinks information and format it for the prompt
#     """
#     food_section_lines = []
    
#     # Add header
#     food_section_lines.append("## Food and Drinks Options")
    
#     # Organize items by category for easier processing
#     items_by_category = {}
#     for category in food_data["categories"]:
#         category_key = category.lower().strip()
#         items_by_category[category_key] = {
#             'items': food_data["items_by_category"][category],
#             'popular': food_data["popular_items_by_category"][category],
#             'other': food_data["other_items_by_category"][category]
#         }
    
#     # Merchandise section
#     merchandise_cats = [cat for cat in items_by_category.keys() if 'merchandise' in cat or 'shirt' in cat or 'socks' in cat]
#     if merchandise_cats:
#         food_section_lines.append("**Merchandise options:**")
#         food_section_lines.append("(These are available as add-ons:)Here are the popular Merchandise options:")
        
#         # Add specific merchandise items
#         merchandise_items = []
#         for cat in merchandise_cats:
#             for item in items_by_category[cat]['popular']:
#                 price_str = f" | Price($):{item['price']}" if item['price'] and item['price'] != 'nan' else ""
#                 merchandise_items.append(f"- {item['item']}{price_str}")
        
#         # Add hardcoded items as per specification
#         food_section_lines.append("- Glow T-shirt | Price($):9.99")
#         food_section_lines.append("- SKYCROCS pair | Price($):70.00")
#         food_section_lines.append("Do you want to know about other Merchandise options? if user says 'yes' then tell below:")
#         food_section_lines.append("- SKYZONE SOCKS | Price($):5.49")
#         food_section_lines.append("")
    
#     # Drinks section
#     drinks_cats = [cat for cat in items_by_category.keys() if 'drink' in cat]
#     if drinks_cats:
#         food_section_lines.append("**Drinks options:**")
#         food_section_lines.append("(These are available as add-ons:)Here are the popular Drinks options:")
        
#         # Add specific drink items
#         for cat in drinks_cats:
#             for item in items_by_category[cat]['popular']:
#                 if 'diet pepsi' in item['item'].lower():
#                     price_str = f" | Price($):{item['price']}" if item['price'] and item['price'] != 'nan' else " | Price($):10.49"
#                     food_section_lines.append(f"- {item['item'].lower()}{price_str}")
#                     break
#         food_section_lines.append("")
    
#     # Pizza section
#     pizza_cats = [cat for cat in items_by_category.keys() if 'pizza' in cat]
#     if pizza_cats:
#         food_section_lines.append("**Pizza(Included In Birthday Party Package) options:**")
#         food_section_lines.append("Here are the popular Pizza options:")
        
#         # Add specific pizza items
#         for cat in pizza_cats:
#             popular_items = items_by_category[cat]['popular']
#             if len(popular_items) >= 2:
#                 # First popular pizza
#                 item1 = popular_items[0]
#                 item_name1 = item1['item']
#                 if 'pepperoni' in item_name1.lower():
#                     price1 = f" | Price($):{item1['price']}" if item1['price'] and item1['price'] != 'nan' else " | Price($):22.00"
#                     food_section_lines.append(f"- Pepperoni Pizza (1 pizza serving for 5 jumpers){price1}")
#                 else:
#                     price1 = f" | Price($):{item1['price']}" if item1['price'] and item1['price'] != 'nan' else ""
#                     food_section_lines.append(f"- {item_name1}{price1}")
                
#                 # Second popular pizza
#                 item2 = popular_items[1]
#                 item_name2 = item2['item']
#                 if 'cheese' in item_name2.lower() or 'pizza' in item_name2.lower():
#                     price2 = f" | Price($):{item2['price']}" if item2['price'] and item2['price'] != 'nan' else " | Price($):20.00"
#                     food_section_lines.append(f"- Pizza1 pizza serving for 5 jumpers{price2}")
#                 else:
#                     price2 = f" | Price($):{item2['price']}" if item2['price'] and item2['price'] != 'nan' else ""
#                     food_section_lines.append(f"- {item_name2}{price2}")
        
#         food_section_lines.append("Do you want to know about other Pizza options? if user says 'yes' then tell below:")
        
#         # Add other pizza items
#         for cat in pizza_cats:
#             other_items = items_by_category[cat]['other']
#             for item in other_items:
#                 if 'sausage' in item['item'].lower():
#                     price_str = f" | Price($):{item['price']}" if item['price'] and item['price'] != 'nan' else " | Price($):22.00"
#                     food_section_lines.append(f"- Sausage Pizza (1 pizza serving for 5 jumpers){price_str}")
#                     break
#         food_section_lines.append("")
    
#     # Party Tray section (first part)
#     party_cats = [cat for cat in items_by_category.keys() if 'party' in cat or 'tray' in cat or 'platter' in cat]
#     if party_cats:
#         food_section_lines.append("**Party Tray options:**")
#         food_section_lines.append("(These are available as add-ons:)Here are the popular Party Tray options:")
        
#         # Add specific party tray items
#         for cat in party_cats:
#             for item in items_by_category[cat]['items']:
#                 item_name = item['item'].lower()
#                 if 'french fry' in item_name:
#                     price_str = f" | Price($):{item['price']}" if item['price'] and item['price'] != 'nan' else " | Price($):16.00"
#                     food_section_lines.append(f"- French Fry platter{price_str}")
#                 elif 'chicken tender' in item_name:
#                     price_str = f" | Price($):{item['price']}" if item['price'] and item['price'] != 'nan' else " | Price($):32.00"
#                     food_section_lines.append(f"- Chicken Tender Platter{price_str}")
#         food_section_lines.append("")
        
#         # Party Tray section (second part)
#         food_section_lines.append("**Party Tray options:**")
#         food_section_lines.append("(These are available as add-ons:)Here are the popular Party Tray options:")
        
#         for cat in party_cats:
#             for item in items_by_category[cat]['items']:
#                 item_name = item['item'].lower()
#                 if 'mini churro' in item_name:
#                     price_str = f" | Price($):{item['price']}" if item['price'] and item['price'] != 'nan' else " | Price($):15.00"
#                     food_section_lines.append(f"- Mini Churro platter{price_str}")
#                     break
#         food_section_lines.append("")
    
#     # Add pricing logic exactly as specified
#     food_section_lines.append("""
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
#     """)
    
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
#     # Organize by category
#     structured_data = {
#         "total_items": len(food_items),
#         "items_by_category": {},
#         "categories": [],
#         "popular_items_by_category": {},
#         "other_items_by_category": {}
#     }
    
#     # Group items by category
#     for item_obj in food_items:
#         category = item_obj.category
#         if category not in structured_data["categories"]:
#             structured_data["categories"].append(category)
#             structured_data["items_by_category"][category] = []
#             structured_data["popular_items_by_category"][category] = []
#             structured_data["other_items_by_category"][category] = []
        
#         item_data = {
#             "item": item_obj.item,
#             "category": item_obj.category,
#             "category_priority": item_obj.category_priority,
#             "category_type": item_obj.category_type or "",
#             "options_type_per_category": item_obj.options_type_per_category or "",
#             "price": str(item_obj.price) if item_obj.price else "",
#             "additional_instructions": item_obj.additional_instructions or "",
#             "t_shirt_sizes": item_obj.t_shirt_sizes or "",
#             "t_shirt_type": item_obj.t_shirt_type or "",
#             "pitch_in_party_package": item_obj.pitch_in_party_package
#         }
        
#         structured_data["items_by_category"][category].append(item_data)
    
#     # Split into popular and other items (first 2 are popular)
#     for category, items in structured_data["items_by_category"].items():
#         structured_data["popular_items_by_category"][category] = items[:2]
#         structured_data["other_items_by_category"][category] = items[2:]
    
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
    food_section_lines.append("## *FOOD & DRINK GUIDELINES*")
    food_section_lines.append("####### Food and Drinks Options")
    
    # Process each category
    for category in food_data["categories"]:
        # Clean category name
        clean_category = category.strip()
        
        # Check category type to determine formatting
        category_type = None
        if clean_category.lower() == "pizza":
            category_type = "included"
        elif clean_category.lower() == "drinks":
            # Check if any drink items have 'included_in_package' type
            for item in food_data["items_by_category"][category]:
                if item.get('category_type') == 'included_in_package':
                    category_type = "included"
                    break
        
        # Format category header based on type
        if category_type == "included":
            food_section_lines.append(f"**{clean_category.title()}(Included In Birthday Party Package) options:**")
            food_section_lines.append(f"Here are the popular {clean_category.title()} options:")
        else:
            food_section_lines.append(f"**{clean_category.title()} options:**")
            # Only show "These are available as add-ons:" for non-included categories
            if clean_category.lower() not in ['pizza', 'drinks']:
                food_section_lines.append(f"(These are available as add-ons:)Here are the popular {clean_category.title()} options:")
            else:
                food_section_lines.append(f"Here are the popular {clean_category.title()} options:")
        
        # Add popular items (first 2 items in category)
        popular_items = food_data["popular_items_by_category"][category]
        for item in popular_items:
            # Format item name with additional instructions if present
            item_name = item['item']
            if item['additional_instructions'] and item['additional_instructions'].lower() != 'nan':
                item_name = f"{item['item']} ({item['additional_instructions']})"
            
            # Format price - handle NaN values
            price = item['price']
            if price and price.lower() != 'nan' and price != 'None':
                price_str = f" | Price($):{price}"
            else:
                price_str = ""
            
            food_section_lines.append(f"- {item_name}{price_str}")
        
        # Add prompt for other items if they exist
        other_items = food_data["other_items_by_category"][category]
        if other_items:
            food_section_lines.append(f"Do you want to know about other {clean_category.title()} options? if user says 'yes' then tell below:")
            for item in other_items:
                # Format item name with additional instructions if present
                item_name = item['item']
                if item['additional_instructions'] and item['additional_instructions'].lower() != 'nan':
                    item_name = f"{item['item']} ({item['additional_instructions']})"
                
                # Format price - handle NaN values
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
        "popular_items_by_category": {},
        "other_items_by_category": {}
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
            x['options_type_per_category'] != 'primary',  # Primary items first
            x['item'].lower()
        ))
        
        structured_data["items_by_category"][normalized_category] = sorted_items
        structured_data["categories"].append(normalized_category)
    
    # Sort categories by priority (lowest first) and then by name
    def get_category_priority(category_name):
        # Find the highest priority (lowest number) in the category
        items = structured_data["items_by_category"][category_name]
        if items:
            return min(item['category_priority'] for item in items)
        return 999
    
    structured_data["categories"] = sorted(
        structured_data["categories"],
        key=lambda cat: (get_category_priority(cat), cat.lower())
    )
    
    # Split into popular and other items (first 2 are popular)
    for category, items in structured_data["items_by_category"].items():
        # For Pizza and Drinks, show 2 popular items; for others, show all as popular
        if category.lower() in ['pizza', 'drinks']:
            structured_data["popular_items_by_category"][category] = items[:2]
            structured_data["other_items_by_category"][category] = items[2:]
        else:
            # For other categories (Merchandise, Party Tray), show all as popular
            structured_data["popular_items_by_category"][category] = items
            structured_data["other_items_by_category"][category] = []
    
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




