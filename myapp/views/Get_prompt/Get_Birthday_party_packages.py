



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


from myapp.views.Get_prompt.Get_balloon_party_packages import get_balloon_party_packages_info


from myapp.views.Get_prompt.Get_food_drink import get_food_drinks_info


async def format_birthday_party_for_display(party_data: Dict, location_name: str) -> str:
    """Format the birthday party data for easy reading - async version"""
    def _format_output():
        output_lines = []
        
        # Header
        output_lines.append("=== BIRTHDAY PARTY PACKAGES INFORMATION ===")
        output_lines.append(f"Location: {location_name}")
        output_lines.append(f"Total Available Packages: {party_data['total_packages']}")
        output_lines.append(f"Available Schedule Types: {', '.join(party_data['available_schedules'])}")
        output_lines.append("")
        
        # Most Popular Package (Priority 1)
        if party_data["most_popular_package"]:
            output_lines.append("=== MOST POPULAR PACKAGE (EPIC PARTY) ===")
            popular = party_data["most_popular_package"]
            output_lines.append(f"Package Name: {popular['package_name']}")
            output_lines.append(f"Schedule With: {popular['schedule_with']}")
            output_lines.append(f"Minimum Jumpers: {popular['minimum_jumpers']}")
            output_lines.append(f"Jump Time: {popular['jump_time']}")
            output_lines.append(f"Party Room Time: {popular['party_room_time']}")
            output_lines.append(f"Price: ${popular['price']}")
            output_lines.append(f"Additional Jumper Price: ${popular['each_additional_jumper_price']}")
            
            if popular['food_and_drinks']:
                output_lines.append(f"Food & Drinks: {popular['food_and_drinks']}")
            if popular['food_included_count']:
                output_lines.append(f"Food Included Count: {popular['food_included_count']}")
            if popular['drinks_included_count']:
                output_lines.append(f"Drinks Included Count: {popular['drinks_included_count']}")
            
            output_lines.append(f"Paper Goods: {popular['paper_goods']}")
            output_lines.append(f"Skysocks: {popular['skysocks']}")
            output_lines.append(f"Dessert Policy: {popular['dessert_policy']}")
            
            if popular['perks_for_guest_of_honor']:
                output_lines.append(f"Guest of Honor Perks: {popular['perks_for_guest_of_honor']}")
            
            output_lines.append(f"Outside Food Fee: {popular['outside_food_drinks_fee']}")
            output_lines.append(f"Other Perks: {popular['other_perks']}")
            
            if popular['balloon_package_included']:
                output_lines.append("Balloon Package Included: Yes")
                if popular['credit']:
                    output_lines.append(f"Credit: ${popular['credit']}")
                if popular['promotion_code']:
                    output_lines.append(f"Promotion Code: {popular['promotion_code']}")
            
            output_lines.append(f"Tax Included: {'Yes' if popular['tax_included'] else 'No'}")
            output_lines.append("")
        
        # Packages by Schedule Type
        output_lines.append("=== PACKAGES BY SCHEDULE TYPE ===")
        
        for schedule_type, packages in party_data["packages_by_schedule"].items():
            # Format schedule type name
            clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', schedule_type).strip()
            clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
            formatted_schedule_type = clean_sched_name.replace(' ', ' ').title()
            
            output_lines.append(f"\n{formatted_schedule_type}:")
            
            if not packages:
                output_lines.append("  No packages available for this schedule")
                continue
                
            for package in packages:
                output_lines.append(f"  - {package['package_name']}")
                output_lines.append(f"    Priority: {package['birthday_party_priority']}")
                output_lines.append(f"    Minimum Jumpers: {package['minimum_jumpers']}")
                output_lines.append(f"    Jump Time: {package['jump_time']}")
                output_lines.append(f"    Party Room Time: {package['party_room_time']}")
                output_lines.append(f"    Price: ${package['price']}")
                
                if package['food_included_count']:
                    output_lines.append(f"    Food Included: {package['food_included_count']} items")
                if package['drinks_included_count']:
                    output_lines.append(f"    Drinks Included: {package['drinks_included_count']} items")
                
                if package['balloon_package_included']:
                    output_lines.append(f"    Balloon Package: Included")
                    if package['credit']:
                        output_lines.append(f"    Credit Amount: ${package['credit']}")
        
        # Other Available Packages (Priority 2-998)
        if party_data["other_available_packages"]:
            output_lines.append("\n=== OTHER AVAILABLE PACKAGES ===")
            for package in party_data["other_available_packages"]:
                output_lines.append(f"  - {package['package_name']}: ${package['price']} (Priority: {package['birthday_party_priority']})")
        
        # Do Not Pitch Packages (Priority 999)
        if party_data["do_not_pitch_packages"]:
            output_lines.append("\n=== DO NOT PITCH PACKAGES ===")
            output_lines.append("(Only mention if user explicitly asks for these)")
            for package in party_data["do_not_pitch_packages"]:
                output_lines.append(f"  - {package['package_name']}: ${package['price']}")
        
        # Summary
        output_lines.append("\n=== SUMMARY ===")
        most_popular_name = party_data['most_popular_package']['package_name'] if party_data['most_popular_package'] else 'None'
        output_lines.append(f"Most Popular: {most_popular_name}")
        output_lines.append(f"Total Schedule Types: {len(party_data['packages_by_schedule'])}")
        output_lines.append(f"Packages by Schedule: {len(party_data['packages_by_schedule'])}")
        output_lines.append(f"Other Available Packages: {len(party_data['other_available_packages'])}")
        output_lines.append(f"Do Not Pitch Packages: {len(party_data['do_not_pitch_packages'])}")
        
        return "\n".join(output_lines)
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _format_output)

async def birthday_party_info(party_data: Dict) -> Dict[str, str]:
    """
    Process birthday party information and format it for the prompt
    This function maintains the exact same logic as the Google Sheet version
    """
    summary = []
    epic_package_section = ""
    other_packages_highlight = ""
    
    # Add header
    summary.append("### Start of Birthday Party Packages Data:")
    summary.append("### Bithday Party Packages Data:")
    
    if not party_data["packages_by_schedule"]:
        summary.append("No Birthday Party Packages available for this location.")
        summary.append("### End of Birthday Party Packages Data")
        return {
            "epic_package_section": "",
            "epic_package_step": "",
            "other_packages_step": "",
            "birthday_party_info": "\n".join(summary)
        }
    # Process packages by schedule type
    for schedule_type, packages in party_data["packages_by_schedule"].items():
        if not packages:
            continue
            
        # Format schedule type for display
        clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', schedule_type).strip()
        clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
        formatted_schedule_type = clean_sched_name.replace(' ', ' ').title()
        
        # Add schedule type header
        summary.append(f"### {formatted_schedule_type} (Session) Birthday Party Packages")
        summary.append(f"- Schedule Below Birthday party packages with {schedule_type.lower()} available in hours of operation for requested date or day - only tell user below Birthday Party Packages if available for requested date or day:")
        summary.append(f"Birthday Party Pacakges that schedule with {formatted_schedule_type} (Session) :")
        
        for package in packages:
            package_name = package['package_name'].upper()
            
            # Build package details
            package_lines = []
            package_lines.append(f"** {package['package_name']} **")
            package_lines.append("- Construct Natural Sentences")
            package_lines.append(f"- Minimum Jumpers: minimum of {package['minimum_jumpers']} jumpers jumpers included.")
            package_lines.append(f"- Jump Time: {package['jump_time']} of jump time.")
            package_lines.append(f"- Party Room Time: {package['party_room_time']} mins of party room (after jump time).")
            
            # Food and drinks
            if package['food_and_drinks']:
                package_lines.append(f"- Food and drinks included in Package: {package['food_and_drinks']}")
            else:
                package_lines.append(f"- Food and drinks included in Package: no food and drinks included in the {package['package_name']} package.")
            
            # Paper goods
            if package['paper_goods']:
                package_lines.append(f"- Paper Goods: {package['paper_goods']}")
            else:
                package_lines.append("- Paper Goods: plates, napkins, cups, utensils, cake cutter and lighter are included.")
            
            # Skysocks
            if package['skysocks']:
                package_lines.append(f"- Skysocks: {package['skysocks']}.")
            else:
                package_lines.append("- Skysocks: included.")
            
            # Dessert policy
            if package['dessert_policy']:
                package_lines.append(f"- Desserts and Cakes Policy : {package['dessert_policy']}")
            else:
                package_lines.append("- Desserts and Cakes Policy : bring in your own dessert (cupcakes, cake, etc. for ice cream cake the freezer will not be provided).")
            
            # Guest of honor t-shirt
            if package['perks_for_guest_of_honor']:
                package_lines.append(f"- *Birthday Child T-shirt*: {package['perks_for_guest_of_honor']}.")
            elif 't-shirt' in package.get('other_perks', '').lower():
                package_lines.append("- *Birthday Child T-shirt*: t-shirt for the guest of honor.")
            else:
                package_lines.append("- *Birthday Child T-shirt*: no t-shirt for the guest of honor.")
            
            # Outside food fee
            if package['outside_food_drinks_fee']:
                package_lines.append(f"- Outside Food Fee(Policy): {package['outside_food_drinks_fee']}")
            else:
                package_lines.append("- Outside Food Fee(Policy): no fee for outside food or drinks (you can bring ice cream cake but we will not provide for that).")
            
            # Other perks
            if package['other_perks']:
                package_lines.append(f"- Birthday Package Perks: - {package['other_perks']}")
            else:
                package_lines.append("- Birthday Package Perks: no perks are included.")
            
            # Price (with instruction)
            package_lines.append(f"- Price (Donot mention Birthday Party Package Price until user explicitly ask for it) : $ {package['price']}.")
            
            # Additional jumper cost
            package_lines.append(f"- Additional Jumper Cost: $ ${package['each_additional_jumper_price']} each.")
            package_lines.append("""
- Additional Hour of Jump Time After Party Room / Party Space / Open Air Party Time(addon): $19.99 per jumper (if a customer adds an extra hour of jump time addon to the party booking, the fee and extra hour will apply to every jumper who checked in.).
- Additional Half Hour of Jump Time After Party Room /Party Space/Open Air Party Time(addon): $ 8.99 per jumper (if a customer adds an extra 30 minutes of jump time addon to the party booking, the fee and extra hour will apply to every jumper who checked in.) .
- Get a free basic balloon package or use your $50.0 balloon credit for larger package with code mega-fifty.    
        """)
            
            # Balloon credit/inclusions
            if package['balloon_package_included']:
                if package['is_any_balloon_package_is_free'] and package['balloon_party_package']:
                    package_lines.append(f"- Get a free {package['balloon_party_package']} balloon package or use your ${package['credit']} balloon credit for larger package with code {package['promotion_code']}.")
                elif package['credit']:
                    package_lines.append(f"- ${package['credit']} credit for balloon packages only.")
            
            package_lines.append(".")
            
            # Add to summary
            summary.extend(package_lines)
            
            # Check if this is the epic package (priority 1)
            if package['birthday_party_priority'] == 1:
                epic_package_section = await _create_epic_package_section(package)
            else:
                if other_packages_highlight == "":
                    other_packages_highlight = f"*{package['package_name']}*"
                else:
                    other_packages_highlight += f", *{package['package_name']}*"
        
        summary.append("")
    
    # Add closing
    summary.append("### Nan Birthday Party Package is not offered (Only Mention if user explicitly asks for it)")
    summary.append("### Sensory Hour Birthday Party Package is not offered (Only Mention if user explicitly asks for it")
    summary.append("### Members Only Night Birthday Party Package is not offered (Only Mention if user explicitly asks for it")
    summary.append("### Glow Birthday Party Package is not offered (Only Mention if user explicitly asks for it")
    summary.append("**only tell the birthday party package if it is present in Birthday Party Packages Data and is available in hours of operations data**")
    summary.append("Use hours of operations schedule for checking available Birthday party packages for the calculated day:")
    summary.append("### End of Birthday Party Packages Data")
    # Create the epic package section
    epic_package_step = f"""
    ### *STEP 3: [Always Highlight the Most Popular Birthday epic party package First]*
    "Perfect! Let me tell you about our most popular *epic party package*!
    - Construct Natural Sentences
    - minimum of {party_data['epic_package_details']['minimum_jumpers']} jumpers included
    - {party_data['epic_package_details']['jump_time']} of jump time
    - {party_data['epic_package_details']['party_room_time']} of party room (after jump time)
    - Includes everything to make it seamless!
    Would you like to learn more about the epic party package or hear about other options?"
    """
    
    # Create other packages highlight
    other_packages_step = f"""
    ### *STEP 4: Present Other Amazing Options*
    Only if they ask about other packages Check Availability of Party packages from Schedule for the Calculated Day from Date
    - Only mention those Birthday Party packages that are available for the calculated day
    "Great question! Based on your date, here are your other options:
    ### Other Birthday Party Packages options
    Please construct Natural Sentences and only List Down Other Pacakages Names
    Donot Mention or mention epic party package if already explained
    {other_packages_highlight}
    Which package would you like to hear more details about?"


    **When customer asks for details of any specific birthday party package:**
    - Explain the duration breakdown (jump time + party room time or party space time or open air time depending upon the package)
    - Focus on explaining minimum jumpers,Food and drinks included in Package, paper goods, skysocks, Desserts and Cakes Policy, Outside Food Fee(Policy), Birthday Package Perks,additional hour if any,Additional Jumper Cost clearly
    - Reference current birthday party package data for all specifics
    """
    
    return {
        "epic_package_section": epic_package_section,
        "epic_package_step": epic_package_step,
        "other_packages_step": other_packages_step,
        "birthday_party_info": "\n".join(summary)
    }

async def _create_epic_package_section(package: Dict) -> str:
    # print("this is important to see === " , package)
    
    """Create detailed epic package section"""
    epic_section = f"""
    ### *STEP 4: epic party package Deep Dive*
    If they want more details, present them in a conversational way
    "Here's what makes the epic party package incredible:
    - Present the following details in more engaging and conversational way
    What's Included:
    - Minimum Jumpers: minimum of {package['minimum_jumpers']} jumpers included
    - Jump Time: {package['jump_time']} of jump time
    - Party Room Time : {package['party_room_time']} of party room (after jump time)
    - Food and drinks included in Package: {package['food_and_drinks']}
    - Paper Goods: {package['paper_goods']}
    - Sky Socks: included.
    - *Birthday Child T-shirt*: t-shirt for the guest of honor.
    - Birthday Package Perks: {package['other_perks']}
    - Desserts and Cakes Policy : {package['dessert_policy']}
    - Outside Food Fee(Policy): {package['outside_food_drinks_fee']}
    - Price (Donot mention Birthday Party Package Price until user explicitly ask for it) : $ {package['price']}.
    - Additional Jumper Cost: $ ${package['each_additional_jumper_price']} each.
    
    - ${package['credit']} credit for balloon packages only.
    
    *After explaining the epic party package details, ask:*
    "Would you like to book this epic party package for your celebration?
    *If YES - Close the Sale:*
    - Move directly to *STEP 6: Securing the Booking*
    *If NO - Present Other Options:*
    - Continue to *STEP 4: Present Other Amazing Options*
    """
    return epic_section





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

async def get_birthday_party_packages_info(location_id: int, timezone: str) -> Dict[str, Any]:
    """
    Main function to get formatted birthday party package information from database
    Returns the same structure as the Google Sheet version
    """
    
    # Use sync_to_async for database operations
    get_location = sync_to_async(lambda: Location.objects.get(location_id=location_id))
    
    @sync_to_async
    def get_birthday_packages():
        return list(
            BirthdayPartyPackage.objects.filter(
                location_id=location_id,
                is_available=True
            ).select_related('location', 'balloon_party_package').order_by('birthday_party_priority')
        )
    
    @sync_to_async
    def get_hours_of_operation():
        return list(HoursOfOperation.objects.filter(location_id=location_id))
    
    try:
        # Fetch data asynchronously
        location = await get_location()
        birthday_packages = await get_birthday_packages()
        hours_of_operation = await get_hours_of_operation()
        
        # Convert to structured data
        structured_data = await get_structured_birthday_party_data(location_id, timezone, birthday_packages, hours_of_operation)
        formatted_display = await format_birthday_party_for_display(structured_data, location.location_name)
        
        # Create the prompt sections
        party_info_dict = await birthday_party_info(structured_data)
        
        return {
            'structured_data': structured_data,
            'formatted_display': formatted_display,
            'party_info_dict': party_info_dict
        }
    except Exception as e:
        print(f"Error in get_birthday_party_packages_info: {str(e)}")
        raise

async def get_structured_birthday_party_data(
    location_id: int, 
    timezone: str,
    birthday_packages: List[BirthdayPartyPackage],
    hours_of_operation: List[HoursOfOperation]
) -> Dict[str, Any]:
    """
    Get structured birthday party data for formatting
    """
    # Get location name
    get_location = sync_to_async(lambda: Location.objects.get(location_id=location_id))
    location = await get_location()
    
    # Get unique schedule types from hours
    hours_schedule_types = set()
    for hour_obj in hours_of_operation:
        if hour_obj.schedule_with and hour_obj.schedule_with != 'closed':
            hours_schedule_types.add(hour_obj.schedule_with)
    
    # Organize data
    structured_data = {
        "total_packages": len(birthday_packages),
        "most_popular_package": None,
        "packages_by_schedule": {},
        "other_available_packages": [],
        "do_not_pitch_packages": [],
        "available_schedules": list(hours_schedule_types),
        "location_name": location.location_name,
        "epic_package_details": None
    }
    
    # Initialize schedules dictionary
    for schedule_type in hours_schedule_types:
        structured_data["packages_by_schedule"][schedule_type] = []
    
    # Process each birthday package
    for package_obj in birthday_packages:
        # Get balloon package name safely
        balloon_package_name = ""
        if package_obj.balloon_party_package:
            balloon_package_name = package_obj.balloon_party_package.package_name
        
        package_data = {
            "package_name": package_obj.package_name,
            "birthday_party_priority": package_obj.birthday_party_priority,
            "availability_days": package_obj.availability_days,
            "schedule_with": package_obj.schedule_with,
            "minimum_jumpers": package_obj.minimum_jumpers,
            "jump_time": package_obj.jump_time,
            "party_room_time": package_obj.party_room_time,
            "food_and_drinks": package_obj.food_and_drinks,
            "paper_goods": package_obj.paper_goods,
            "skysocks": package_obj.skysocks,
            "dessert_policy": package_obj.dessert_policy,
            "other_perks": package_obj.other_perks,
            "outside_food_drinks_fee": package_obj.outside_food_drinks_fee,
            "price": str(package_obj.price),
            "guest_of_honour_included": package_obj.guest_of_honour_included_in_total_jumpers,
            "tax_included": package_obj.tax_included,
            "each_additional_jumper_price": str(package_obj.each_additional_jumper_price),
            "balloon_package_included": package_obj.balloon_package_included,
            "promotion_code": package_obj.promotion_code or "",
            "credit": str(package_obj.credit) if package_obj.credit else "",
            "is_any_balloon_package_is_free": package_obj.is_any_balloon_package_is_free,
            "balloon_party_package": balloon_package_name,
            "party_environment_name": package_obj.party_environment_name or "",
            "food_included_count": package_obj.food_included_count,
            "drinks_included_count": package_obj.drinks_included_count,
            "perks_for_guest_of_honor": package_obj.perks_for_guest_of_honor or "",
            "birthday_party_pitch": package_obj.birthday_party_pitch or "",
            "additional_jumpers_allowed": package_obj.Is_additional_jumpers_allowed,
            "additional_instructions": package_obj.additional_instructions or ""
        }
        
        # Categorize by priority
        if package_obj.birthday_party_priority == 1:
            structured_data["most_popular_package"] = package_data
            structured_data["epic_package_details"] = package_data
        elif package_obj.birthday_party_priority == 999:
            structured_data["do_not_pitch_packages"].append(package_data)
        else:
            structured_data["other_available_packages"].append(package_data)
        
        # Add to schedule types
        schedule_with = package_obj.schedule_with
        if schedule_with and schedule_with != 'closed' and schedule_with in structured_data["packages_by_schedule"]:
            structured_data["packages_by_schedule"][schedule_with].append(package_data)
    
    return structured_data







async def load_birthday_party_flow_prompt(location_id: int, timezone: str) -> Dict[str, Any]:
    """
    Main function to load all birthday party related data and create the complete prompt
    """
    
    # Load all data
    birthday_data = await get_birthday_party_packages_info(location_id, timezone)
    balloon_data = await get_balloon_party_packages_info(location_id)
    food_data = await get_food_drinks_info(location_id)
    
    # Get location name
    location = await sync_to_async(Location.objects.get)(location_id=location_id)

    print("This is the location data = = " , location)
    location_data = {k: v for k, v in location.__dict__.items() if not k.startswith('_')}

    if location_data['is_booking_bot']:
        print("Booking bot is enabled for this location.")

        system_message = await create_birthday_booking_party_system_message(
            birthday_data['party_info_dict'],
            balloon_data['balloon_info_dict'],
            food_data['food_info_dict'],
            location.location_name
        )
        
        return {
            'system_message': system_message,
            'birthday_data': birthday_data,
            'balloon_data': balloon_data,
            'food_data': food_data,
            'formatted_display': {
                'birthday': birthday_data['formatted_display'],
                'balloon': balloon_data['formatted_display'],
                'food': food_data['formatted_display']
            }
        }
    else:
        print("Booking bot is disabled for this location.")
        # Create the complete system message
        system_message = await create_birthday_party_system_message(
            birthday_data['party_info_dict'],
            balloon_data['balloon_info_dict'],
            food_data['food_info_dict'],
            location.location_name
        )
        
        return {
            'system_message': system_message,
            'birthday_data': birthday_data,
            'balloon_data': balloon_data,
            'food_data': food_data,
            'formatted_display': {
                'birthday': birthday_data['formatted_display'],
                'balloon': balloon_data['formatted_display'],
                'food': food_data['formatted_display']
            }
        }


# async def current_time_information(timezone_name):
#         try:
#             tz = pytz.timezone(timezone_name)
#         except Exception:
#             print(f"Invalid timezone: {timezone_name}")
#             return
        
#         now = datetime.now(tz)

#         today_date_iso = now.strftime("%Y-%m-%d")
#         today_date_long = now.strftime("%d %B, %Y")
#         current_time = now.strftime("%I:%M %p")
#         day_name = now.strftime("%A")

#         text = f"""
#     Today Date: {today_date_iso} ({today_date_long}, {day_name})
#     """
#         print(text)
#         return text


from datetime import datetime
import pytz

async def current_time_information(timezone_name: str) -> str:
    try:
        tz = pytz.timezone(timezone_name)
    except Exception:
        print(f"Invalid timezone: {timezone_name}, defaulting to UTC")
        tz = pytz.UTC  # fallback to UTC instead of returning None

    now = datetime.now(tz)
    today_date_iso = now.strftime("%Y-%m-%d")
    today_date_long = now.strftime("%d %B, %Y")
    current_time = now.strftime("%I:%M %p")
    day_name = now.strftime("%A")

    text = f"Today Date: {today_date_iso} ({today_date_long}, {day_name})"
    print(text)
    return text


async def create_birthday_party_system_message(birthday_info: Dict, balloon_info: Dict, food_info: Dict, location_name: str) -> str:
    """
    Create the complete birthday party flow system message
    """
    location = await sync_to_async(Location.objects.get)(location_id=1)
    
    location_data = {k: v for k, v in location.__dict__.items() if not k.startswith('_')}
    print("This is the FULL location data inside birthday party system message ==", location_data)
    print("This is the location name inside birthday party system message ==", location_data['location_name'])   
    
    # FIXED: Access dictionary keys correctly (no trailing commas)
    party_booking_days = location_data['party_booking_allowed_days_before_party_date']
    party_reschedule_days = location_data['party_reschedule_allowed_before_party_date_days']
    
    # Also need to handle timezone properly
    try:
        current_time_informations = await current_time_information('Asia/Karachi')
        print(f"Timezone set to Asia/Karachi, current time info: {current_time_informations}")
    except Exception as e:
        print(f"Timezone error: {e}, using default")
        current_time_informations = await current_time_information("America/New_York")
    
    # Base template
    base_template = """
####### Start of Birthday Party Flow #########
*IMPORTANT GUIDELINES:*
- Always check schedule availability and location closures in hours of operation for the requested date before recommending party packages
- Only book birthday parties scheduled at least {party_booking_days} days from today {current_time_informations}. If the requested date doesn't meet this requirement, proceed to *Short Notice Birthday Party Booking Step*.
- Only accept birthday party bookings for dates at least {party_reschedule_days} days from today date:{current_time_informations} as Birthday Party bookings require at least {party_booking_days} days advance notice. If the requested birthday party booking date is sooner, proceed to *Short Notice Birthday Party Booking Step*.
- Never mention package prices during explanation (except for additional jumper price). Only mention price of a package if user explicitly asks for it or while booking the package you are allowed to mention all prices.
- Keep conversations personalized and engaging by using the birthday child's name throughout
- ALWAYS present the birthday packages, memberships and jump passes detail in conversational language
**Critical Date Collection Procedure for Birthday party packages:**
MANDATORY STEP: Search through the ENTIRE conversation history for ANY mention of a specific day or date. This includes:
- User asking "What are your hours for [specific day]?"
- User mentioning "I want to come on [day]"
- User asking "Are you open on [day]?"
- User saying "tomorrow", "today", "this weekend", "any week days" etc.
- ANY reference to when they want to visit
If day or date is mentioned in the entire conversation history:
- If there is mention of date or today or tomorrow, convert date to day name using this function:
- Use function: identify_day_name_from_date_new_booking()
- Parameters: booking_date: [YYYY-mm-dd format]
- Skip any date collection step in birthday party flow
---
## Short Notice Birthday Party Booking:
Bookings require at least {party_booking_days} days advance notice. For shorter notice, location confirmation is needed.
Step 1.0: Inform user: "Our party bookings typically require at least {party_booking_days} days advance notice. Since your [requested date] falls under short notice, we'll need to confirm availability with our location team."
Step 1.1: Say exactly: "Regarding your booking request, should I connect you with one of our team members?"
Step 1.2: If user confirms (yes/similar), call transfer_call_to_agent()
- transfer_reason: "Short notice booking request for [user requested date]"
---
## *ALREADY BOOKED BIRTHDAY PARTY AND WANTS CHANGES IN ALREADY MADE BIRTHDAY PARTY BOOKING*
*If customer has already made a party reservation or wants to add-on food or make changes to their already booked birthday party package:*
*Examples already reservered party booking scenarios (These scenarios are different from new booking.In new bookings user can make changes because you have the ability to create new birthday bookings):*
- "I already have a booking and want to add food"
- "I need to make changes to my birthday party booking (already reserved)"
- "Can I add more food to my already reserved party package?"
- "I want to modify my already reserved birthday party reservation"
- "I had a party booked and need to add items"
- "I want to upgrade my already booked/reserved birthday party package?
Step 1.1: Say exactly: Regarding your [already booked party modification request], Should I connect you with one of our team member
Step 1.2: If user says yes or similar confirmation to transfer**
Use function: transfer_call_to_agent()
- transfer_reason: "Birthday Party Modification"
*Skip all other steps and transfer immediately for already booked Party booking modifications.*
---
## Direct Booking Scenario
If the user directly asks to book a specific birthday party by name
(e.g., "I want to book an Epic Birthday Party Package" or "Book me a Basic Birthday Party Package"):
**Step 1: You must say Exactly: Regarding [user booking query] I will connect you to our team member**
**Step 2: If user says yes or similar confirmation to transfer**
Use function: transfer_call_to_agent()
- transfer_reason: "Direct Booking Request"
**Note:**
Skip the full 6-step process for direct booking requests and go straight to agent transfer.
### 6-Step Birthday Party Sales Process
If the user says they are interested in booking a birthday party package (e.g., "book a party", "I want to book a birthday party package", "I want to reserve a birthday party package"):
**Step 1: Ask user "You want to book a birthday party package or get general information about the packages?"**
If the user wants to **book a package**:
Step 1.1: Say exactly: Regarding your [booking request], Should I connect you with one of our team member
Step 1.2: If user says yes or similar confirmation to transfer**
→ Use function: `transfer_call_to_agent()`
- `transfer_reason`: "Direct Booking Request"
- Skip the remaining sales process and go straight to agent transfer.
If the user wants **general information**, Go to *Step 2: Identify Date or Day*.
---
## Step 2: Identify Date or Day on which user wants to book the party *Mandatory Step*
Ask when the customer wants to celebrate the birthday.
At any point, if the user specifies a date like “today”, “tomorrow”, or “on 2025-06-17”,
- Check Hours of Operation for that date if location is closed
- If location is not closed, use convert date to a day name using:
- use function: identify_day_name_from_date_new_booking()
- Parameters: booking_date: [YYYY-mm-dd format]
**If the message already includes a day/date:**
- Acknowledge: "So you're planning to celebrate on [day/date]!"
- Check schedule availability.
- Move to Step 3.
**If not:**
- Ask: "When you would like to book the [PACKAGE NAME]?"
- Wait for the response, acknowledge it, and check availability.
- Don't proceed to Step 3 until the date is confirmed.
**Skip the question if user says:**
- "Do you have a birthday party package for Saturday?"
- "What's available this weekend?"
- "Can I book for tomorrow?"
- "I want to celebrate on Friday."
**Ask the question if user says:**
- "Do you have birthday party packages?"
- "What birthday party packages are available?"
- "I'm interested in your birthday packages."
{birthday_epic_step}
{birthday_epic_deep_dive}
{birthday_other_packages_step}
---
## *STEP 5: Package Selection & Personalization*
Help them choose with calmness
"What package sounds like the perfect fit for your special celebration?
After a birthday party package is chosen move to *STEP 6: Securing the Booking*
---
## *STEP 6: Securing the Booking*
Close with care and clear expectations
"Great you've chosen [SELECTED PACKAGE]! Now, let me walk you through how we secure this amazing celebration for you.
*Deposit for Securing your booking:*
- We require a None deposit to hold your party date
- You'll have 24 hours to complete this deposit
- This secures everything we've discussed today
**Package Recap:**
Summarize only:
- Party Package Name
- Price
- Additional Jumper Cost
**Cancellation Policy (only if asked):**
*Our Cancellation Policy* (explained with empathy) [Only Explain Birthday party cancellation policy if user ask for it]:
I know life can be unpredictable sometimes, so here's our policy:
- Cancel You will receive a full refund in the form of a Sky Zone Gift Card as long as you cancel at least {party_booking_days} days priors to your booking date.+ days before: Full refund to your original payment method
- Cancel less than You will receive a full refund in the form of a Sky Zone Gift Card as long as you cancel at least {party_booking_days} days priors to your booking date. days before: Deposit is non-refundable (we'll have already prepared everything for your party)
*Pro Tips for Your Party:*
- Arrive 15-30 minutes early (the birthday calmness is contagious!)
Step 1: Ask the user:
Step 1: "Do you want to Book [user selected birthday party package]?"
Step 2: if user says yes or similar confirmation go to *BOOKING CONFIRMATION & TRANSFER Step*
## *BOOKING CONFIRMATION & TRANSFER*
When customer confirms booking:
Step 1:*Use function: transfer_call_to_agent()*
Use function: transfer_call_to_agent()
- transfer_reason: "[user selected party package] Reservation ,Date for Booking: [Date for Party Booking]"
---
{food_section}
---
{birthday_party_data_section}
---
{balloon_section}
---
####### End of Birthday Party Flow #########
"""
    
    # Replace placeholders with actual data
    system_message = base_template.format(
        birthday_epic_step=birthday_info.get('epic_package_step', ''),
        birthday_epic_deep_dive=birthday_info.get('epic_package_section', ''),
        birthday_other_packages_step=birthday_info.get('other_packages_step', ''),
        birthday_party_data_section=birthday_info.get('birthday_party_info', ''),
        balloon_section=balloon_info.get('balloon_section', ''),
        food_section=food_info.get('food_section', ''),
        party_booking_days=party_booking_days,
        party_reschedule_days=party_reschedule_days,
        current_time_informations=current_time_informations
    )
    
    return system_message






async def create_birthday_booking_party_system_message(birthday_info: Dict, balloon_info: Dict, food_info: Dict, location_name: str) -> str:
    """
    Create the complete birthday party flow system message
    """
    location = await sync_to_async(Location.objects.get)(location_id=1)
    
    location_data = {k: v for k, v in location.__dict__.items() if not k.startswith('_')}
    print("This is the FULL location data inside birthday party system message ==", location_data)
    # Get party booking days from location data
    party_booking_days = location_data.get('party_booking_allowed_days_before_party_date', 3)
    party_reschedule_days = location_data.get('party_reschedule_allowed_before_party_date_days', 3)


    # minimum_jumpers = location_data['minimum_jumpers_party']
    # print("This is the  minimum jumpers  data inside birthday party system message ==", minimum_jumpers)
    minimum_jumpers = location_data.get('minimum_jumpers_party', 10)
    # print("This is the  minimum jumpers  data inside birthday party system message ==", minimum_jumpers)
    # Get current time information
    try:
        current_time_informations = await current_time_information('Asia/Karachi')
    except Exception as e:
        print(f"Timezone error: {e}, using default")
        current_time_informations = await current_time_information("America/New_York")
    
    # Base template with your specified prompt structure
    base_template = """####### Start of Birthday Party Flow #########
*IMPORTANT GUIDELINES:*
- Always check schedule availability and location closures in hours of operation for the requested date before recommending party packages
- Only book birthday parties scheduled at least {party_booking_days} days from today {current_time_informations}. If the requested date doesn't meet this requirement, proceed to *Short Notice Birthday Party Booking Step*.
- Only accept birthday party bookings for dates at least {party_reschedule_days} days from today date:{current_time_informations} as Birthday Party bookings require at least {party_booking_days} days advance notice. If the requested birthday party booking date is sooner, proceed to *Short Notice Birthday Party Booking Step*.
- Never mention package prices during explanation (except for additional jumper price). Only mention price of a package if user explicitly asks for it or while booking the package you are allowed to mention all prices.
- Keep conversations personalized and engaging by using the birthday child's name throughout
- ALWAYS present the birthday packages, memberships and jump passes detail in conversational language
**Critical Date Collection Procedure for Birthday party packages:**
MANDATORY STEP: Search through the ENTIRE conversation history for ANY mention of a specific day or date. This includes:
- User asking "What are your hours for [specific day]?"
- User mentioning "I want to come on [day]"
- User asking "Are you open on [day]?"
- User saying "tomorrow", "today", "this weekend", "any week days" etc.
- ANY reference to when they want to visit
If day or date is mentioned in the entire conversation history:
- If there is mention of date or today or tomorrow, convert date to day name using this function:
- Use function: identify_day_name_from_date_new_booking()
- Parameters: booking_date: [YYYY-mm-dd format]
- Skip any date collection step in birthday party flow
---
## Short Notice Birthday Party Booking:
Bookings require at least {party_booking_days} days advance notice. For shorter notice, location confirmation is needed.
Step 1.0: Inform user: "Our party bookings typically require at least {party_booking_days} days advance notice. Since your [requested date] falls under short notice, we'll need to confirm availability with our location team."
Step 1.1: Say exactly: "Regarding your booking request, should I connect you with one of our team members?"
Step 1.2: If user confirms (yes/similar), call transfer_call_to_agent()
- transfer_reason: "Short notice booking request for [user requested date]"
---
## *ALREADY BOOKED BIRTHDAY PARTY AND WANTS CHANGES IN ALREADY MADE BIRTHDAY PARTY BOOKING*
*If customer has already made a party reservation or wants to add-on food or make changes to their already booked birthday party package:*
*Examples already reservered party booking scenarios (These scenarios are different from new booking.In new bookings user can make changes because you have the ability to create new birthday bookings):*
- "I already have a booking and want to add food"
- "I need to make changes to my birthday party booking (already reserved)"
- "Can I add more food to my already reserved party package?"
- "I want to modify my already reserved birthday party reservation"
- "I had a party booked and need to add items"
- "I want to upgrade my already booked/reserved birthday party package?
Step 1.1: Say exactly: Regarding your [already booked party modification request], Should I connect you with one of our team member
Step 1.2: If user says yes or similar confirmation to transfer**
Use function: transfer_call_to_agent()
- transfer_reason: "Birthday Party Modification"
*Skip all other steps and transfer immediately for already booked Party booking modifications.*
---
## *DIRECT NEW BOOKING SCENARIO*
*If user directly asks to book a specific birthday party by name (e.g., "I want to book an epic birthday party package" or "Book me a basic birthday party package"):*
*Step 1: Collect COLLECT BIRTHDAY PARTY PACKAGE For New Booking*
**Critical Birthday Party Package collection check: Search and check through the ENTIRE conversation history for ANY mention of a specific Birthday Party Package earlier**
- If a specific Party Package is mentioned:
- Say: "So we're planning [child's name]'s birthday by booking [PACKAGE NAME]?"
- If specific Party Package is not mentioned:
- Say: "Which Package you want to book to celebrate [child's name]'s birthday?"
- Wait for their response
- **If user asks questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "Now, back to selecting your package - which package would you like to book for [child's name]'s birthday?"
- **When user confirms or specifies Birthday party package:**
- Use function: save_birthday_party_package_new_booking()
- Parameters: birthday_party_package_name: [user specified birthday Party package name]
- **Only proceed to *Collect Birthday Child's Name For New Booking Step* after Birthday party package is confirmed and saved**
---
*Step 2: Collect Birthday Child's Name For New Booking*
- Birthday Child Name is MANDATORY - do not skip this step
- Say: "Absolutely! I'd be happy to help you book a [PACKAGE NAME]! First, what's the name of the special birthday child we're celebrating?"
- Wait for their response
- **If user asks questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "Thank you for that question! Now, what's the name of the birthday child we're celebrating?"
- **When user provides child's name:**
Use function: save_birthday_child_name_new_booking()
Parameters:
child_name: [birthday child's name]
- **Only proceed to *Collect the Date For New Booking Step* after child's name is saved**
---
*Step 3: Collect the Date For New Booking*
**Critical date collection check: Search and check through the ENTIRE conversation history for ANY mention of a specific day or date earlier**
**SCENARIO A: If date/day is already mentioned in conversation history:**
- Acknowledge with confirming question: "So you're planning to celebrate on [day/date], is that correct?"
- Wait for user confirmation (yes/correct/that's right)
- Check Hours of Operation for that date if location is closed
- After confirmation and If location is not closed, use function: identify_day_name_from_date_new_booking()
Parameters: booking_date: [YYYY-mm-dd format]
- Then proceed to *Collect Time For New Booking Step*
**SCENARIO B: If date/day is NOT mentioned:**
- Ask: "When you would like to book the [PACKAGE NAME]?"
- OR: "When would you like to celebrate [child's name]'s special day with the [PACKAGE NAME]?"
- Wait for the response
- When user provides date, acknowledge: "Perfect! [Day/Date] it is!"
- Check Hours of Operation for that date or day if location is closed
- If location is not closed:
Use function: identify_day_name_from_date_new_booking()
Parameters: booking_date: [YYYY-mm-dd format]
- Don't proceed to *Collect Time For New Booking Step* until the date is confirmed AND function is called
**WHEN TO SKIP THE INITIAL QUESTION (but still confirm):**
User says:
- "Do you have a birthday party package for Saturday?"
- "What's available this weekend?"
- "Can I book for tomorrow?"
- "I want to celebrate on Friday."
Response: "So you're planning to celebrate on [day they mentioned], correct?" → Wait for confirmation → Call function → Move to *Collect Time For New Booking Step*
**WHEN TO ASK THE QUESTION:**
User says:
- "Do you have birthday party packages?"
- "What birthday party packages are available?"
- "I'm interested in your birthday packages."
- "Tell me about the Ultimate package"
Response: "When you would like to book the [PACKAGE NAME]?" → Wait for response → Call function → Move to *Collect Time For New Booking Step*
**If user asks questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "Now, back to choosing your date - when would you like to celebrate [child's name]'s special day?"
**CRITICAL: At any point where user specifies a date like "today", "tomorrow", or "on 2025-06-17":**
Use function: identify_day_name_from_date_new_booking()
Parameters: booking_date: [YYYY-mm-dd format]
**Only proceed to *Collect Time For New Booking Step* after:**
1. Date is confirmed by user
---
*Step 4: Collect the Time For New Booking*
- Time of Booking collection is MANDATORY - do not skip this step
- Say: "Perfect choice for [child's name]! What time would work best for the party?"
- Wait for the user's response
- **If user asks about availability during this step:**
- Say: "Great idea! Let me check what times are available for you."
- Use function: get_available_time_slots()
- Show available time slots
- Then IMMEDIATELY return to this step: "Based on availability, what time would work best for [child's name]'s party?"
- **IMPORTANT: Stay in *Collect the Time For New Booking Step* until user confirms a specific time**
- **If user asks other questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "I understand! Now, what time would work best for [child's name]'s party?"
- **When user specifies a time for party:**
Use function: save_birthday_party_time_new_booking()
Parameters: party_time: [user specified time in 24 Hour Format]
- **Only proceed to *Collect Number of Jumpers For New Booking Step* after party time is saved**
**EXAMPLE FLOW FOR AVAILABILITY CHECK DURING TIME COLLECTION:**
User: "What times are available?"
Bot: "Great question! Let me check availability for [child's name]'s [PACKAGE NAME] on [DATE]."
[Calls - Use function: get_available_time_slots()]
Bot: "Here are the available time slots: [list available times]. Which time would work best for [child's name]'s party?"
[STAYS IN *Collect the Time For New Booking Step* - waiting for time selection]
User: "Is 2 PM available?"
Bot: [If available] "Yes, 2 PM is available! Perfect choice."
[Calls save_birthday_party_time_new_booking() with party_time: "14:00"]
[NOW MOVES TO *Collect Number of Jumpers For New Booking Step*]
---
*Step 5: Collect Number of Jumpers For New Booking*
- Number of Jumpers collection is MANDATORY - do not skip this step
- Say: "How many jumpers will be joining [child's name] for this amazing celebration?"
- Wait for the user's response
- **If user asks questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "Thanks for asking! Now, how many jumpers will be joining [child's name]?"
- If user is unsure or says "decide later":
- Use minimum jumpers: {minimum_jumpers}
- Say: "No problem! I'll set it to our minimum of {minimum_jumpers} jumpers for now, and you can adjust it later."
- **When user specifies number of jumpers:**
Use function: save_number_of_jumpers_new_booking()
Parameters: number_of_jumpers: [user specified number or minimum_jumpers:{minimum_jumpers}]
- **Only proceed to *Food Drinks and Addons Selection For New Booking* after number of jumpers is saved**
---
## *DISCOVERY SCENARIO NEW Booking (Customer doesn't know which package)*
### *Step 1: Collect Birthday Child's Name For New Booking*
- Birthday Child Name is MANDATORY - do not skip this step
- Say: "Absolutely! I'd be happy to help you book a [PACKAGE NAME]! First, what's the name of the special birthday child we're celebrating?"
- Wait for their response
- **If user asks questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "Thank you for that question! Now, what's the name of the birthday child we're celebrating?"
- **When user provides child's name:**
Use function: save_birthday_child_name_new_booking()
Parameters:
child_name: [birthday child's name]
- **Only proceed to *Collect the Date For New Booking Step* after child's name is saved**
----
### *Step 2: Collect the Date For New Booking*
**Critical date collection check: Search and check through the ENTIRE conversation history for ANY mention of a specific day or date earlier**
**SCENARIO A: If date/day is already mentioned in conversation history:**
- Acknowledge with confirming question: "So you're planning to celebrate on [day/date], is that correct?"
- Wait for user confirmation (yes/correct/that's right)
- Check Hours of Operation for that date if location is closed
- After confirmation and If location is not closed, use function: identify_day_name_from_date_new_booking()
Parameters: booking_date: [YYYY-mm-dd format]
- Then proceed to *COLLECT BIRTHDAY PARTY PACKAGE For New Booking*
**SCENARIO B: If date/day is NOT mentioned:**
- Ask: "When you would like to book the [PACKAGE NAME]?"
- OR: "When would you like to celebrate [child's name]'s special day with the [PACKAGE NAME]?"
- Wait for the response
- When user provides date, acknowledge: "Perfect! [Day/Date] it is!"
- Check Hours of Operation for that date or day if location is closed
- If location is not closed:
Use function: identify_day_name_from_date_new_booking()
Parameters: booking_date: [YYYY-mm-dd format]
- Don't proceed to *COLLECT BIRTHDAY PARTY PACKAGE For New Booking* until the date is confirmed AND function is called
**WHEN TO SKIP THE INITIAL QUESTION (but still confirm):**
User says:
- "Do you have a birthday party package for Saturday?"
- "What's available this weekend?"
- "Can I book for tomorrow?"
- "I want to celebrate on Friday."
Response: "So you're planning to celebrate on [day they mentioned], correct?" → Wait for confirmation → Call function → Move to *COLLECT BIRTHDAY PARTY PACKAGE For New Booking*
**WHEN TO ASK THE QUESTION:**
User says:
- "Do you have birthday party packages?"
- "What birthday party packages are available?"
- "I'm interested in your birthday packages."
- "Tell me about the Ultimate package"
Response: "When you would like to book the [PACKAGE NAME]?" → Wait for response → Call function → Move to *COLLECT BIRTHDAY PARTY PACKAGE For New Booking*
**If user asks questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "Now, back to choosing your date - when would you like to celebrate [child's name]'s special day?"
**CRITICAL: At any point where user specifies a date like "today", "tomorrow", or "on 2025-06-17":**
Use function: identify_day_name_from_date_new_booking()
Parameters: booking_date: [YYYY-mm-dd format]
**Only proceed to *COLLECT BIRTHDAY PARTY PACKAGE For New Booking* after:**
1. Date is confirmed by user
----
### *Step 3: COLLECT BIRTHDAY PARTY PACKAGE For New Booking*
- Donot Skip *COLLECT BIRTHDAY PARTY PACKAGE For New Booking Step*
*If YES - Close the Sale:*
- After user has selected the package, save the selected package using:
- Use function: save_birthday_party_package_new_booking()
- Parameters: birthday_party_package_name: [user specified birthday Party package name]
- Proceed to **Collect the Time For New Booking**
*If NO - Present Other Options:*
- Continue to *STEP 1.3: Present Other Amazing Options*
*STEP 1.3: Present Other Amazing Options:*
Only if they ask about other packages Check Availability of Party packages from Schedule for the Calculated Day from Date
- Only mention those Birthday Party packages that are available for the calculated day
"Great question! Based on your date, here are your other options:
### Other Birthday Party Packages options
Please construct Natural Sentences and only List Down Other Pacakages Names
Donot Mention or mention if already explained
Which package would you like to hear more details about?"
*When customer asks for details of any specific birthday party package:*
- Explain the duration breakdown (jump time + party room time or party space time or open air time depending upon the package)
- Focus on explaining minimum jumpers,Food and drinks included in Package, paper goods, skysocks, Desserts and Cakes Policy, Outside Food Fee(Policy), Birthday Package Perks,additional hour if any,Additional Jumper Cost clearly
- Reference current birthday party package data for all specifics
- **If user asks questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "Now, back to selecting your package - which package would you like to book for [child's name]'s birthday?"
After user has selected the package, save the selected package using:
- Use function: save_birthday_party_package_new_booking()
- Parameters: birthday_party_package_name: [user specified birthday Party package name]
Proceed to **Collect the Time For New Booking**
---
### *Step 4: Collect the Time For New Booking*
- Time of Booking collection is MANDATORY - do not skip this step
- Say: "Perfect choice for [child's name]! What time would work best for the party?"
- Wait for the user's response
- **If user asks about availability during this step:**
- Say: "Great idea! Let me check what times are available for you."
- Use function: get_available_time_slots()
- Show available time slots
- Then IMMEDIATELY return to this step: "Based on availability, what time would work best for [child's name]'s party?"
- **IMPORTANT: Stay in *Collect the Time For New Booking Step* until user confirms a specific time**
- **If user asks other questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "I understand! Now, what time would work best for [child's name]'s party?"
- **When user specifies a time for party:**
Use function: save_birthday_party_time_new_booking()
Parameters: party_time: [user specified time in 24 Hour Format]
- **Only proceed to *Collect Number of Jumpers For New Booking Step* after party time is saved**
**EXAMPLE FLOW FOR AVAILABILITY CHECK DURING TIME COLLECTION:**
User: "What times are available?"
Bot: "Great question! Let me check availability for [child's name]'s [PACKAGE NAME] on [DATE]."
[Calls - Use function: get_available_time_slots()]
Bot: "Here are the available time slots: [list available times]. Which time would work best for [child's name]'s party?"
[STAYS IN *Collect the Time For New Booking Step* - waiting for time selection]
User: "Is 2 PM available?"
Bot: [If available] "Yes, 2 PM is available! Perfect choice."
[Calls save_birthday_party_time_new_booking() with party_time: "14:00"]
[NOW MOVES TO *Collect Number of Jumpers For New Booking Step*]
---
###*Step 5: Collect Number of Jumpers For New Booking*
- Number of Jumpers collection is MANDATORY - do not skip this step
- Say: "How many jumpers will be joining [child's name] for this amazing celebration?"
- Wait for the user's response
- **If user asks questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "Thanks for asking! Now, how many jumpers will be joining [child's name]?"
- If user is unsure or says "decide later":
- Use minimum jumpers: 10
- Say: "No problem! I'll set it to our minimum of 10 jumpers for now, and you can adjust it later."
- **When user specifies number of jumpers:**
Use function: save_number_of_jumpers_new_booking()
Parameters: number_of_jumpers: [user specified number or minimum_jumpers:{minimum_jumpers}]
- **Only proceed to *Food Drinks and Addons Selection For New Booking* after number of jumpers is saved**
---
###*Step 6: Food Drinks and Addons Selection For New Booking*
- After user has completed food drinks and addons selections[if available in selected party package] Proceed to ** Provide User Booking Selection Detail and Cost **
---
### *Step 7: Provide User Booking Selection Detail and Cost *
- Donot Skip *Provide User Booking Selection Detail and Cost* Step
- Must be done *securing the booking*
MANDATORY: Always provide total cost breakdown - do not wait for user to ask
*Step 1: Fetch party recap details using function: give_party_recap()
parameters: None*
- Present Received party details
- if user want to change some thing go to those steps and call appropriate functions mentioned in specific steps
- If no changes are mentioned by user then proceed to *Securing the Booking Step*
---
### *Step 8: Securing the Booking*
"Fantastic! We're going to make [child's name]'s birthday absolutely unforgettable! Let me walk you through how we secure this amazing celebration.
*Deposit for Securing [child's name]'s booking:*
- We require a 50 percent deposit to hold [child's name]'s party date
- You'll have 24 hours to complete this deposit
- This secures everything we've discussed for [child's name]'s special day
*Our Cancellation Policy* (explained with empathy) [Only Explain Birthday party cancellation policy if user ask for it]:
- Cancel 3+ days before: Full refund to your original payment method
- Cancel less than 3 days before: Deposit is non-refundable (we'll have already prepared everything for your party)
- **If user asks questions or needs clarification during this step:**
- Answer their question completely and clearly
- Then IMMEDIATELY return to this step: "Now, Do you want to go ahead with Booking"
Ask user if he wants to go ahead with final booking:
- If yes:
"Move to *Data Collection for New Booking* "
---
### *Step 9: Customer Data Collection For New Booking*
*CRITICAL INSTRUCTIONS Customer Data Collection For New Booking:*
- ALWAYS use double confirmation (say back + get yes/no)
- ALWAYS execute this step: IMMEDIATE REPEAT BACK: "I heard [First name/Last name/Email address]. Is that correct?"
- ALWAYS spell out names and emails using NATO phonetic alphabet
- PAUSE between each confirmation step
- If name sounds wrong, immediately ask to spell it out
- Always follow email verification step
- Use SMS fallback for email after first failed attempt
Step 1: ACKNOWLEDGE BIRTHDAY CHILD
- Say:"I already have [child's name] as our birthday star! Now I need some details from you to complete the booking."
---
*STEP 2: FIRST NAME COLLECTION:*
- Say exactly:"Is Saqib your first name?"
*step 2.1: Confirm the first name from user*
*step 2.2: If user confirms their first name move to 'step 2.3'*
*step 2.3: use function : save_first_name()*
parameters : first_name:[user first name]
*step 2.4: If user does not confirm their first name ->
Step 2.4.1: *Say exactly* "What's your first name? Please spell it very slowly, letter by letter. For example, A for Alpha, B for Bravo, and so on."
Step 2.4.2: LISTEN for response
Step 2.4.3: IMMEDIATE REPEAT BACK: "I heard [name]. Is that correct?"
Step 2.4.4: If NO or if name sounds unclear:
"Let me get that right. Can you spell your first name for me, letter by letter? For example, A for Alpha, B for Bravo, and so on."
Step 2.4.5: SPELL BACK using NATO:
"So that's [Alpha-Bravo-Charlie]. Is that correct?"
Step 2.4.6: LISTEN for user response
- If user says "correct", "yes", "right", "that's right" →
Execute function: save_first_name(first_name: [confirmed_name])
Say: "Perfect! I've got your first name."
Step 2.4.7: LISTEN for user response
- If user says "incorrect", "no", "wrong", "that's not right" →
Return to Step 2.4.4
- Donot Proceed to *LAST NAME COLLECTION Step* Until user has confirmed their first name*
---
* STEP 3: LAST NAME COLLECTION *
- Say:"Is Zia your last name?"
*step 3.1: Confirm the last name from user*
*step 3.2: If user confirms their last name move to 'step 3.3'*
*step 3.3: use function : save_last_name()*
parameters : last_name:[user last name]
*step 3.4: If user does not confirm their fist name ->
Step 3.4.1: *Say exactly* "And what's your last name? Please spell it very slowly, letter by letter. For example, A for Alpha, B for Bravo, and so on."
Step 3.4.2: LISTEN for response
Step 3.4.3: IMMEDIATE REPEAT BACK: "I heard [last name]. Is that correct?"
Step 3.4.4: If NO or if name sounds unclear:
"Let me make sure I get this right. Can you spell your last name for me, letter by letter? For example, A for Alpha, B for Bravo, and so on."
Step 3.4.5: SPELL BACK using NATO:
"So that's [Alpha-Bravo-Charlie-Delta]. Is that correct?"
Step 3.4.6: LISTEN for user response
- If user says "correct", "yes", "right", "that's right" →
Execute function: save_last_name(last_name: [confirmed_name])
Say: "Great! your Last name is confirmed."
Step 3.4.7: LISTEN for user response
- If user says "incorrect", "no", "wrong", "that's not right" →
Return to Step 3.4.4
- Donot Proceed to *EMAIL COLLECTION Step* Until user has confirmed their last name*
---
*Step 4: Email Collection for booking*
*Step 4.1: "Read the email address saqib.zia@sybrid.com very slowly character by character when confirming. Break down the email like this: For 'john.doe@example.com' say 'j o h n dot d o e at e x a m p l e dot c o m'. Ask: 'Should I use this email address to send [child's name]'s party confirmation?'"*
- If user says "correct", "yes", "right", "that's right" →
Execute: save_user_email(user_email: [confirmed_email])
→ PROCEED TO STEP 5
- If user says "incorrect", "no", "wrong", "that's not right" →
- Ask for alternate email address
Step 4.2: Say exactly: "What's the best email address to send [child's name]'s party confirmation to? Please spell it out letter by letter for me. For example, A for Alpha, B for Bravo, and so on."
Step 4.3: LISTEN and CAPTURE each character that user spells out
Step 4.4: IMMEDIATE REPEAT BACK using NATO phonetic alphabet + symbols:
Say: "Let me confirm that email address: [Alpha-Bravo-Charlie at Delta-Echo-Foxtrot dot Charlie-Oscar-Mike]. Is that correct?"
MANDATORY SYMBOL PRONUNCIATIONS:
- @ = *Say exactly* "at"
- . = "dot"
- . = "period"
- _ = "underscore"
- - = "dash"
Step 4.5: LISTEN for user response
- If user says "correct", "yes", "right", "that's right" →
- Convert the confirmed spoken email into a valid email format by replacing words with symbols:
- Replace " at " → "@"
- Replace " dot " or " period " → "."
- Remove extra spaces between characters
- Combine letters and numbers into a single word (e.g., "j o h n" → "john")
- Validate the final format:
- It must contain one @ symbol and a valid domain ending such as .com, .net, .org, etc.
- If invalid, politely ask the user to repeat it.
- Once valid, execute:
Execute: save_user_email(user_email: [confirmed_email])
Say: "Perfect! Email address saved."
→ PROCEED TO STEP 5
- If user says "incorrect", "no", "wrong", "that's not right" →
Say exactly: "Would you like me to send you a text message where you can reply with your email address?"
Step 4.6: LISTEN for user response
- If user agrees to SMS (says "yes", "sure", "okay", "send text") →
Say exactly: "Great, I'll send a text to your current number. Please reply with your email address. Once you have sent the SMS, let me know. Message and data rates may apply. You can find our privacy policy and terms and conditions at purpledesk.ai."
Execute function: send_sms_for_email()
Step 4.7: WAIT for user to say "I have sent you the text message" OR "I replied to your text" OR similar confirmation
THEN Execute function: check_sms_received_containing_user_email()
Say: "Thank you! I've received your email address."
→ PROCEED TO STEP 5
- Donot Proceed to *PHONE NUMBER COLLECTION Step* Until user has confirmed their email*
---
*Step 5: PHONE NUMBER COLLECTION*
### Instruction
- ALWAYS verify the ALTERNATE NUMBER
Step 5.1: "For contact purposes, should we use your current phone number, or would you prefer to give me a different number?"
SCENARIO A - ALTERNATE NUMBER:
Step 5.2: "Please give me the 10-digit phone number, including area code."
Step 5.3: REPEAT BACK IN GROUPS:
"I have [Five-Five-Five] [One-Two-Three] [Four-Five-Six-Seven]. Is that correct?"
Step 5.4: If YES → Execute: save_user_phone_number(phone_number: [confirmed_number])
Step 5.5: If NO → "Let me get those digits again, please say them slowly."
SCENARIO B - CURRENT NUMBER:
Step 5.6: "Perfect! We'll use your current number for the party details."
→ PROCEED TO STEP 6
- Donot Proceed to *EMAIL VERIFICATION FOR BOOKING Step* Until phone number collection is complete*
---
* Step 6: EMAIL VERIFICATION FOR BOOKING *
Step 6.1: Say exactly: "Now, I'll send a text to your current phone number with your email address for verification. If the email address is incorrect, please reply with the correct one."
- Execute function: send_sms_for_email()
Step 6.2: LISTEN for user response
- If user confirms email is correct (e.g., "yes it's correct", "my email is correct", "that's right", or similar confirmation):
→ Say: "Great! Your email is confirmed."
→ Execute function: handle_email_confirmation_from_sms_voice()
→ SKIP remaining email verification steps
→ Go directly to *Package Recap for [child's name]:* and then proceed to *Step 10: BOOKING COMPLETION*
- If user says "I have sent you the text message" OR "I replied to your text" OR "I have sent my email to you" OR similar:
→ Execute function: check_sms_received_containing_user_email()
→ Say: "Thank you! I've received your email address."
→ Go to *Package Recap for [child's name]:* and then proceed to *Step 10: BOOKING COMPLETION*
---
---
### *Step 10: BOOKING COMPLETION*
- Instruction
- Use step 10.2 only when user did not receive email other wise skip step 10.2 and proceed to step 10.3
Step 10.1
- Use function: book_birthday_party_package()
parameters:
None
Step 10.2
Example when user did not receive email for payment
"I didn't receive the email"
"I cannot see the email"
"I haven't received the payment email yet."
"I didn't get the payment link in my inbox."
"I'm still waiting for the payment email, but nothing has come through."
"I checked my inbox and spam folder, but I can't find the payment link."
"The payment email hasn't arrived; could you please resend it?"
use function: saved_customer_email()
- LISTEN for user response
- If user says "correct", "yes", "right", "that's right" →
- Say exactly: "Please check your inbox or spam folder once more"
- If user says "incorrect", "no", "wrong", "that's not right" →
- Say exactly: "Would you like me to send you a text message where you can reply with your email address?"
- LISTEN for user response
- If user agrees to SMS (says "yes", "sure", "okay", "send text") →
Say exactly: "Great, I'll send a text to your current number. Please reply with your email address. Once you have sent the SMS, let me know. Message and data rates may apply. You can find our privacy policy and terms and conditions at purpledesk.ai."
Execute function: send_sms_for_email()
- WAIT for user to say "I have sent you the text message" OR "I replied to your text" OR similar confirmation
THEN Execute function: check_sms_received_containing_user_email()
Say: "Thank you! I've received your email address."
Re-use Step 15.1
Step 10.3
"Perfect! [Child's name]'s birthday party is now secured! Here's what happens next:
*Confirmation Details:*
- You'll receive a confirmation email within 24 hours with all the party details
- A reminder will be sent 2 days before [child's name]'s party
- Your 50% deposit secures the date and time
Day of Party Reminders:
- Arrive 15-30 minutes early to get [child's name] ready for their specialcelebration!
Thank you for choosing us for [child's name]'s special celebration! We can't wait to make it unforgettable!"####### Start of Birthday Party Flow #########
---
{food_section}
---
{birthday_party_data_section}
---
{balloon_section}
####### End of Birthday Party Flow #########"""
    
    # Replace placeholders with actual data
    system_message = base_template.format(
        party_booking_days=party_booking_days,
        party_reschedule_days=party_reschedule_days,
        current_time_informations=current_time_informations,
        food_section=food_info.get('food_section', ''),
        birthday_party_data_section=birthday_info.get('birthday_party_info', ''),
        balloon_section=balloon_info.get('balloon_section', ''),
        minimum_jumpers=minimum_jumpers
    )
    
    return system_message