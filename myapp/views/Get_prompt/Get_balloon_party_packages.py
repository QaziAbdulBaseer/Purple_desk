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




async def format_balloon_party_for_display(balloon_data: Dict, location_name: str) -> str:
    """Format the balloon party data for easy reading - async version"""
    def _format_output():
        output_lines = []
        
        # Header
        output_lines.append("=== BALLOON PARTY PACKAGES INFORMATION ===")
        output_lines.append(f"Location: {location_name}")
        output_lines.append(f"Total Available Packages: {balloon_data['total_packages']}")
        output_lines.append("")
        
        # Most Popular Package (Priority 1)
        if balloon_data["most_popular_package"]:
            output_lines.append("=== MOST POPULAR BALLOON PACKAGE ===")
            popular = balloon_data["most_popular_package"]
            output_lines.append(f"Package Name: {popular['package_name']}")
            output_lines.append(f"Price: ${popular['price']}")
            
            if popular['promotional_pitch']:
                output_lines.append(f"Promotional Pitch: {popular['promotional_pitch']}")
            if popular['package_inclusions']:
                output_lines.append(f"Inclusions: {popular['package_inclusions']}")
            if popular['discount']:
                output_lines.append(f"Discount: {popular['discount']}")
            if popular['note']:
                output_lines.append(f"Note: {popular['note']}")
            
            output_lines.append("")
        
        # Other Available Packages
        if balloon_data["other_available_packages"]:
            output_lines.append("=== OTHER AVAILABLE BALLOON PACKAGES ===")
            for package in balloon_data["other_available_packages"]:
                output_lines.append(f"  - {package['package_name']}: ${package['price']}")
                if package['promotional_pitch']:
                    output_lines.append(f"    Pitch: {package['promotional_pitch']}")
        
        # Do Not Pitch Packages
        if balloon_data["do_not_pitch_packages"]:
            output_lines.append("\n=== DO NOT PITCH BALLOON PACKAGES ===")
            output_lines.append("(Only mention if user explicitly asks for these)")
            for package in balloon_data["do_not_pitch_packages"]:
                output_lines.append(f"  - {package['package_name']}: ${package['price']}")
        
        # All Packages Details
        output_lines.append("\n=== ALL BALLOON PACKAGES DETAILS ===")
        for package in balloon_data["all_packages"]:
            output_lines.append(f"\n*{package['package_name']}* :")
            output_lines.append(f"  Balloons Included: {package['package_inclusions']}")
            output_lines.append(f"  Discount: {package['discount']}")
            output_lines.append(f"  Price: {package['price']}")
        
        return "\n".join(output_lines)
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _format_output)




async def balloon_party_info(balloon_data: Dict) -> Dict[str, str]:
    """
    Process balloon party information and format it for the prompt
    """
    # Build the balloon packages section
    balloon_section_lines = []
    
    # Add header
    balloon_section_lines.append("### Start of Party Balloon Booking Flow ###")
    balloon_section_lines.append("- Present Balloon Packages in in a conversational way")
    balloon_section_lines.append("""
*Step 1:*check If user wants to add decorational Balloons to [child name Birthday Party**
-Ask:"We have some amazing Balloon options that you can add to decorate your [child name] birthday celebration.Do you want to hear about Balloon Packages?"
- If user says "yes" then proceed to *Step 2*
*Step 1: Determine whether the user wants to add decorative balloons to [child name]'s birthday party*
-Ask: "We have some amazing balloon options that can add a festive touch to [child name]'s birthday celebration. Would you like to hear about our Balloon Packages?"
-If the user responds "yes", proceed to *Step 2*.    
""")
    
    # Most popular balloon package section
    if balloon_data["most_popular_package"]:
        popular = balloon_data["most_popular_package"]
        balloon_section_lines.append(f"""
#*STEP: 2* [Always Highlight the Most Popular {popular['package_name']} First]*
-It includes: {popular['package_inclusions']}
-Ask user:"Would you like to hear more details about {popular['package_name']} or hear about other Balloon packages too?"
- If user asks about other Balloon Packages Go to Present Other Party Balloons Options***:
        """)
    
    # Other packages
    other_packages = []
    for package in balloon_data["other_available_packages"]:
        other_packages.append(package['package_name'])
    
    if other_packages:
        balloon_section_lines.append(f"""
# *STEP 3: Present Other Party Balloons Options*
"Great question! here are your other options:
{', '.join(other_packages)}
If user wants to know about any ballon package use this ballon data to explain interested ballon packages in a conversation flow:
        """)
    
    # All packages details
    balloon_section_lines.append("Ballon Packages:")
    for package in balloon_data["all_packages"]:
        balloon_section_lines.append(f"""
*{package['package_name']}* :
Ballons Included: {package['package_inclusions']}
Discount : {package['discount']}
Price: {package['price']}
        """)
    
    # Booking process
    balloon_section_lines.append("""
Balloon Add in Booking Process:
*At any point If user wants to book balloon packages:
**Step 1: You must say Exactly: regarding [Ballon Package selected by user] booking, Should I connect you to one of our team member**
**Step 2: If user says yes or similar confirmation**
Use function: transfer_call_to_agent()
- transfer_reason: "[Balloon Package selected by user] Booking Request"
### Ballon Policy (Only if user asks):
- Credits are not transferrable and non refundable and credits can only be used to buy ballon packages and are these credits cannot be used for Birthday party packages
- please note that all products must be ordered at least 24 hours in advance of your event to ensure timely preparation and delivery. we appreciate your understanding and look forward to making your event a success!
### END of Party Balloon Booking Flow ###
    """)
    
    return {
        "balloon_section": "\n".join(balloon_section_lines)
    }

async def get_balloon_party_packages_info(location_id: int) -> Dict[str, Any]:
    """
    Main function to get formatted balloon party package information from database
    """
    
    @sync_to_async
    def get_balloon_packages():
        return list(
            BalloonPartyPackage.objects.filter(
                location_id=location_id
            ).select_related('location').order_by('call_flow_priority')
        )
    
    @sync_to_async
    def get_location():
        return Location.objects.get(location_id=location_id)
    
    try:
        # Fetch data asynchronously
        balloon_packages = await get_balloon_packages()
        location = await get_location()
        
        # Convert to structured data
        structured_data = await get_structured_balloon_party_data(location_id, balloon_packages)
        formatted_display = await format_balloon_party_for_display(structured_data, location.location_name)
        
        # Create the prompt sections
        balloon_info_dict = await balloon_party_info(structured_data)
        
        return {
            'structured_data': structured_data,
            'formatted_display': formatted_display,
            'balloon_info_dict': balloon_info_dict
        }
    except Exception as e:
        print(f"Error in get_balloon_party_packages_info: {str(e)}")
        raise






async def get_structured_balloon_party_data(
    location_id: int,
    balloon_packages: List[BalloonPartyPackage]
) -> Dict[str, Any]:
    """
    Get structured balloon party data for formatting
    """
    # Organize data
    structured_data = {
        "total_packages": len(balloon_packages),
        "most_popular_package": None,
        "other_available_packages": [],
        "do_not_pitch_packages": [],
        "all_packages": []
    }
    
    # Process each balloon package
    for package_obj in balloon_packages:
        package_data = {
            "package_name": package_obj.package_name,
            "call_flow_priority": package_obj.call_flow_priority,
            "promotional_pitch": package_obj.promotional_pitch or "",
            "package_inclusions": package_obj.package_inclusions or "",
            "discount": package_obj.discount or "",
            "price": str(package_obj.price),
            "note": package_obj.note or ""
        }
        
        structured_data["all_packages"].append(package_data)
        
        # Categorize by priority
        if package_obj.call_flow_priority == 1:
            structured_data["most_popular_package"] = package_data
        elif package_obj.call_flow_priority == 999:
            structured_data["do_not_pitch_packages"].append(package_data)
        else:
            structured_data["other_available_packages"].append(package_data)
    
    return structured_data

