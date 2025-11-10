
# Get_prompt/Get_jump_pass.py

import pandas as pd
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from myapp.model.jump_passes_model import JumpPass
from myapp.model.hours_of_operations_model import HoursOfOperation
from myapp.model.locations_model import Location
from asgiref.sync import sync_to_async
import json

async def get_jump_pass_info(location_id: int, timezone: str) -> dict:
    """
    Main function to get formatted jump pass information from database
    Returns the same structure as the Google Sheet version
    """
    
    # Fetch jump passes from database
    jump_passes = await sync_to_async(list)(
        JumpPass.objects.filter(location_id=location_id).order_by('jump_pass_priority')
    )
    
    # Fetch hours of operation from database
    hours_of_operation = await sync_to_async(list)(
        HoursOfOperation.objects.filter(location_id=location_id)
    )
    
    # Fetch location name
    location = await sync_to_async(Location.objects.get)(location_id=location_id)
    
    # Convert to DataFrames to maintain compatibility with existing code
    jump_pass_data = []
    for pass_obj in jump_passes:
        # Handle schedule_with field - convert list to string for DataFrame compatibility
        schedule_with = pass_obj.schedule_with
        if isinstance(schedule_with, list):
            schedule_with_str = ",".join(schedule_with)
        else:
            schedule_with_str = str(schedule_with) if schedule_with else ""
            
        jump_pass_data.append({
            'pass_name': pass_obj.pass_name,
            'schedule_with': schedule_with_str,  # Convert list to string
            'age_allowed': pass_obj.age_allowed,
            'jump_time_allowed': pass_obj.jump_time_allowed,
            'price': float(pass_obj.price),
            'recommendations': pass_obj.recommendation,
            'pitch_introduction': pass_obj.jump_pass_pitch or "",
            'pitch_priority': pass_obj.jump_pass_priority,
            'starting_day_name': pass_obj.starting_day_name or "",
            'ending_day_name': pass_obj.ending_day_name or "",
            'availability_days': 'always' if not pass_obj.starting_day_name and not pass_obj.ending_day_name else 'certain_days',
            'tax_included': pass_obj.tax_included,
            'can_custom_take_part_in_multiple': pass_obj.can_custom_take_part_in_multiple,
            'comments': pass_obj.comments or ""
        })
    
    hours_data = []
    for hour_obj in hours_of_operation:
        hours_data.append({
            'jump_type': hour_obj.schedule_with
        })
    
    # Create DataFrames
    df = pd.DataFrame(jump_pass_data)
    hours_df = pd.DataFrame(hours_data)
    
    # Use the existing function with the DataFrames
    schedule_with_dict = {}  # This was in original code but not used, keeping for compatibility
    
    result = await jump_pass_info(df, schedule_with_dict, hours_df)
    
    # Add formatted display using the new function
    structured_data = await get_structured_jump_pass_data(location_id, timezone)
    formatted_display = await format_jump_passes_for_display(structured_data, location.location_name)
    
    # Add to result
    result['formatted_display'] = formatted_display
    result['structured_data'] = structured_data
    
    return result


async def get_structured_jump_pass_data(location_id: int, timezone: str) -> Dict[str, Any]:
    """
    Get structured jump pass data for formatting
    """
    # Fetch jump passes from database
    jump_passes = await sync_to_async(list)(
        JumpPass.objects.filter(location_id=location_id).order_by('jump_pass_priority')
    )
    
    # Organize data by schedule type and priority
    structured_data = {
        "total_passes": len(jump_passes),
        "most_popular_pass": None,
        "passes_by_schedule": {},
        "other_available_passes": [],
        "do_not_pitch_passes": [],
        "unavailable_schedules": []
    }
    
    # Get all unique schedule types from jump passes
    all_schedule_types = set()
    for pass_obj in jump_passes:
        schedule_with = pass_obj.schedule_with
        if isinstance(schedule_with, list):
            for schedule in schedule_with:
                if schedule and schedule != 'closed':
                    all_schedule_types.add(schedule)
        elif schedule_with and schedule_with != 'closed':
            all_schedule_types.add(schedule_with)
    
    # Initialize passes_by_schedule structure
    for schedule_type in all_schedule_types:
        structured_data["passes_by_schedule"][schedule_type] = []
    
    # Process each jump pass
    for pass_obj in jump_passes:
        pass_data = {
            "pass_name": pass_obj.pass_name,
            "age_allowed": pass_obj.age_allowed,
            "jump_time_allowed": pass_obj.jump_time_allowed,
            "price": str(pass_obj.price),
            "recommendation": pass_obj.recommendation or "",
            "jump_pass_pitch": pass_obj.jump_pass_pitch or "",
            "starting_day_name": pass_obj.starting_day_name or "",
            "ending_day_name": pass_obj.ending_day_name or "",
            "tax_included": pass_obj.tax_included,
            "can_custom_take_part_in_multiple": pass_obj.can_custom_take_part_in_multiple,
            "comments": pass_obj.comments or "",
            "jump_pass_priority": pass_obj.jump_pass_priority
        }
        
        # Categorize by priority
        if pass_obj.jump_pass_priority == 1:
            structured_data["most_popular_pass"] = pass_data
        elif pass_obj.jump_pass_priority == 999:
            structured_data["do_not_pitch_passes"].append(pass_data)
        else:
            structured_data["other_available_passes"].append(pass_data)
        
        # Add to schedule types
        schedule_with = pass_obj.schedule_with
        if isinstance(schedule_with, list):
            for schedule in schedule_with:
                if schedule and schedule != 'closed' and schedule in structured_data["passes_by_schedule"]:
                    structured_data["passes_by_schedule"][schedule].append(pass_data)
        elif schedule_with and schedule_with != 'closed' and schedule_with in structured_data["passes_by_schedule"]:
            structured_data["passes_by_schedule"][schedule_with].append(pass_data)
    
    # Get unavailable schedules (schedules in hours but not in jump passes)
    hours_of_operation = await sync_to_async(list)(
        HoursOfOperation.objects.filter(location_id=location_id)
    )
    
    hours_schedule_types = set()
    for hour_obj in hours_of_operation:
        if hour_obj.schedule_with and hour_obj.schedule_with != 'closed':
            hours_schedule_types.add(hour_obj.schedule_with)
    
    structured_data["unavailable_schedules"] = list(hours_schedule_types - all_schedule_types)
    
    return structured_data


async def format_jump_passes_for_display(jump_pass_data: Dict, location_name: str) -> str:
    """Format the jump pass data for easy reading - async version"""
    def _format_output():
        output_lines = []
        
        # Current info section
        output_lines.append("=== JUMP PASSES INFORMATION ===")
        output_lines.append(f"Location: {location_name}")
        output_lines.append(f"Total Available Passes: {jump_pass_data['total_passes']}")
        output_lines.append("")
        
        # Most Popular Pass (Priority 1)
        if jump_pass_data["most_popular_pass"]:
            output_lines.append("=== MOST POPULAR PASS ===")
            popular = jump_pass_data["most_popular_pass"]
            output_lines.append(f"Pass Name: {popular['pass_name']}")
            output_lines.append(f"Jump Time: {popular['jump_time_allowed']}")
            output_lines.append(f"Ages Allowed: {popular['age_allowed']}")
            output_lines.append(f"Price: ${popular['price']}")
            if popular['recommendation']:
                output_lines.append(f"Recommendation: {popular['recommendation']}")
            if popular['jump_pass_pitch']:
                output_lines.append(f"Pitch: {popular['jump_pass_pitch']}")
            
            # Add availability information
            if popular['starting_day_name'] and popular['ending_day_name']:
                output_lines.append(f"Available: {popular['starting_day_name']} to {popular['ending_day_name']}")
            elif popular['starting_day_name']:
                output_lines.append(f"Available: {popular['starting_day_name']}")
            else:
                output_lines.append(f"Available: Always")
            
            if popular['tax_included']:
                output_lines.append(f"Tax Included: Yes")
            else:
                output_lines.append(f"Tax Included: No")
                
            if popular['can_custom_take_part_in_multiple']:
                output_lines.append(f"Multiple Schedule: Yes")
            
            output_lines.append("")
        
        # Passes by Schedule Type
        output_lines.append("=== PASSES BY SCHEDULE TYPE ===")
        
        for schedule_type, passes in jump_pass_data["passes_by_schedule"].items():
            # Format schedule type name
            clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', schedule_type).strip()
            clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
            formatted_schedule_type = clean_sched_name.replace(' ', ' ').title()
            
            output_lines.append(f"\n{formatted_schedule_type}:")
            
            if not passes:
                output_lines.append("  No passes available")
                continue
                
            for pass_item in passes:
                output_lines.append(f"  - {pass_item['pass_name']}")
                output_lines.append(f"    Jump Time: {pass_item['jump_time_allowed']}")
                output_lines.append(f"    Ages: {pass_item['age_allowed']}")
                output_lines.append(f"    Price: ${pass_item['price']}")
                
                # Add availability information
                if pass_item['starting_day_name'] and pass_item['ending_day_name']:
                    output_lines.append(f"    Available: {pass_item['starting_day_name']} to {pass_item['ending_day_name']}")
                elif pass_item['starting_day_name']:
                    output_lines.append(f"    Available: {pass_item['starting_day_name']}")
                else:
                    output_lines.append(f"    Available: Always")
                
                if pass_item['recommendation']:
                    output_lines.append(f"    Recommendation: {pass_item['recommendation']}")
                
                if pass_item['tax_included']:
                    output_lines.append(f"    Tax Included: Yes")
                else:
                    output_lines.append(f"    Tax Included: No")
                    
                if pass_item['can_custom_take_part_in_multiple']:
                    output_lines.append(f"    Multiple Schedule: Yes")
                
                if pass_item['comments']:
                    output_lines.append(f"    Comments: {pass_item['comments']}")
                
                priority_display = "Do not pitch" if pass_item['jump_pass_priority'] == 999 else pass_item['jump_pass_priority']
                output_lines.append(f"    Priority: {priority_display}")
        
        # Other Available Passes (Priority 2-998)
        if jump_pass_data["other_available_passes"]:
            output_lines.append("\n=== OTHER AVAILABLE PASSES ===")
            for pass_item in jump_pass_data["other_available_passes"]:
                availability_note = ""
                if pass_item['starting_day_name'] and pass_item['ending_day_name']:
                    availability_note = f" (Available {pass_item['starting_day_name']} to {pass_item['ending_day_name']})"
                elif pass_item['starting_day_name']:
                    availability_note = f" (Available {pass_item['starting_day_name']})"
                
                output_lines.append(f"  - {pass_item['pass_name']}{availability_note}: {pass_item['jump_time_allowed']} for {pass_item['age_allowed']} - ${pass_item['price']}")
        
        # Do Not Pitch Passes (Priority 999)
        if jump_pass_data["do_not_pitch_passes"]:
            output_lines.append("\n=== DO NOT PITCH PASSES ===")
            output_lines.append("(Only mention if user explicitly asks for these)")
            for pass_item in jump_pass_data["do_not_pitch_passes"]:
                output_lines.append(f"  - {pass_item['pass_name']}: {pass_item['jump_time_allowed']} for {pass_item['age_allowed']} - ${pass_item['price']}")
        
        # Unavailable Schedule Types
        if jump_pass_data["unavailable_schedules"]:
            output_lines.append("\n=== UNAVAILABLE SCHEDULE TYPES ===")
            output_lines.append("(No jump passes offered for these schedule types)")
            for schedule_type in jump_pass_data["unavailable_schedules"]:
                clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', schedule_type).strip()
                clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
                formatted_schedule_type = clean_sched_name.replace(' ', ' ').title()
                output_lines.append(f"  - {formatted_schedule_type}")
        
        # Summary
        output_lines.append("\n=== SUMMARY ===")
        most_popular_name = jump_pass_data['most_popular_pass']['pass_name'] if jump_pass_data['most_popular_pass'] else 'None'
        output_lines.append(f"Most Popular: {most_popular_name}")
        output_lines.append(f"Total Schedule Types: {len(jump_pass_data['passes_by_schedule'])}")
        output_lines.append(f"Other Available Passes: {len(jump_pass_data['other_available_passes'])}")
        output_lines.append(f"Do Not Pitch Passes: {len(jump_pass_data['do_not_pitch_passes'])}")
        output_lines.append(f"Unavailable Schedule Types: {len(jump_pass_data['unavailable_schedules'])}")
        
        return "\n".join(output_lines)
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _format_output)


async def jump_pass_info(df: pd.DataFrame, schedule_with_dict: dict, hours_df: pd.DataFrame) -> dict:
    """
    Process jump pass information and format it for the prompt
    This function maintains the exact same logic as the Google Sheet version
    """
    summary = []
    
    # Get unique schedule_with values - handle both string and list types
    schedule_with_values = []
    for sched in df['schedule_with']:
        if isinstance(sched, str) and sched.strip():
            # Split comma-separated values and extend the list
            schedule_with_values.extend([x.strip() for x in sched.split(',') if x.strip()])
        elif isinstance(sched, list):
            # If it's already a list, extend directly
            schedule_with_values.extend([x for x in sched if x])
    
    # Remove duplicates and get unique values
    schedule_with_values = list(set(schedule_with_values))
    
    # Get unique jump types from hours
    hours_jump_type_unique_values = []
    for jump_type in hours_df['jump_type']:
        if pd.notna(jump_type) and str(jump_type).strip():
            hours_jump_type_unique_values.append(str(jump_type).strip())
    hours_jump_type_unique_values = list(set(hours_jump_type_unique_values))
    
    most_popular_pass_prompt = ""
    other_jump_passes_prompt = "### Other Jump pass options"
    other_jump_passes_prompt += "\n Please construct Natural Sentences and only List Passes Names"
    
    other_jump_passes_available_always = ""
    other_jump_passes_available_certain_days = ""
    other_jump_passes_donot_mention_until_asked = ""

    ## case birthday package is available for jump type but jump pass is not available
    jump_passes_available_for_jumping = []
    
    for sched in schedule_with_values:
        # Filter DataFrame for this schedule - check if schedule_with contains the value
        df_sched = df[df['schedule_with'].apply(
            lambda x: sched in (x.split(',') if isinstance(x, str) else x) if pd.notna(x) else False
        )]
        
        if df_sched.empty:
            continue
            
        # Create clean section header
        clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', sched).strip()
        clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
        section_title = clean_sched_name.replace(' ', ' ').title()
        section_title = section_title + " Hours (Session)"

        scheduling_instruction = f"""Schedule Below Jump passes or Jump tickets with {sched.replace('_',' ')} available in hours of operation for requested date or day - only tell user this pass if available for requested date or day"""

        summary.append(f"#### {section_title} Jump Passes")
        summary.append(scheduling_instruction)
        summary.append(f"Passes information that schedule with {section_title}:")
        summary.append("")

        if sched not in jump_passes_available_for_jumping:
            jump_passes_available_for_jumping.append(sched)
        
        # Group passes by type for better organization
        pass_details = []
        for _, row in df_sched.iterrows():
            pass_name = row['pass_name']
            pass_name_temp = pass_name
            temp_recommendations = row["recommendations"]
            recommendations = ""
            
            if temp_recommendations and pd.notna(temp_recommendations) and str(temp_recommendations).strip() and str(temp_recommendations) != "nan":
                recommendations = f"({temp_recommendations})"
                
            starting_day = row["starting_day_name"]
            ending_day = row["ending_day_name"]
            
            starting_day_and_ending_day = ""
            if starting_day and ending_day and pd.notna(starting_day) and pd.notna(ending_day):
                if str(starting_day).strip() and str(ending_day).strip() and str(starting_day).lower() != "nan" and str(ending_day).lower() != "nan":
                    starting_day_and_ending_day = f"| Available Days : {starting_day} to {ending_day}"
            
            if recommendations.strip():
                pass_name = f" {pass_name}  {recommendations}   " 
                    
            age = row['age_allowed']
            jump_time = row['jump_time_allowed']
            # price = str(row['price']).strip().replace('.', ' point ')
            price = str(row['price']).strip()

            # Handle the decimal point replacement
            if '.' in price:
                # Split into whole and decimal parts
                parts = price.split('.')
                whole_part = parts[0]
                decimal_part = parts[1] if len(parts) > 1 else ''
                
                # If decimal part is just '0' or empty, use only whole part
                if decimal_part in ('0', '00', ''):
                    price = whole_part
                else:
                    # For actual decimals, use ' point '
                    price = whole_part + ' point ' + decimal_part
            
            # Now use this formatted price
            introductory_pitch = row["pitch_introduction"]
            priority = row["pitch_priority"]
            availability = row["availability_days"]
            
            # Handle priority - ensure it's integer
            try:
                priority_int = int(priority)
            except (ValueError, TypeError):
                priority_int = 999  # Default to don't pitch if invalid
                
            if priority_int == 1:
                most_popular_pass_prompt = f"""1. **[Always Present The {introductory_pitch} {jump_time} {pass_name_temp} for {age} First]:**
                - Calculate the day from selected date
                - Present the {introductory_pitch} {jump_time} {pass_name_temp} {recommendations} for {age} as the primary option:
                    - **Say Exactly:** "For our most popular pass, the {jump_time} {pass_name_temp} for {age}, you get {jump_time} of jump time for $[price of 90-Minute standard pass]."
                    - **Say Exactly Do not change any words:** "We have other jump passes as well - would you like to hear about those options or would you like to purchase the standard pass?"
                    - **Say Exactly Do not change any words:**"Just to let you know, memberships offer big savings compared to buying individual passes."""
                    
            elif priority_int == 999:
                # Don't add to prompt - don't mention until asked
                pass
            else:
                if availability == "always":
                    other_jump_passes_available_always += f"""\n - Pass Name:{pass_name_temp} {recommendations} | Introductory Pitch:{introductory_pitch} | jump time:{jump_time} | ages for: {age} """
                else:
                    other_jump_passes_available_certain_days += f"""\n - Pass Name:{pass_name_temp}( {pass_name_temp} is available on certain days Please check schedule of hours of operations before mentioning {pass_name_temp}) {recommendations} | Introductory Pitch:{introductory_pitch} | jump time:{jump_time} | ages for: {age} """
            
            if not isinstance(pass_name, str) or pass_name.strip() == "":
                continue
            
            # Create detailed entry
            entry = f"- **{pass_name.strip()}** {starting_day_and_ending_day} | Price : ${price} | Ages Allowed: {age.lower()} | Jump Time: {jump_time}"
            pass_details.append(entry)

        # Add all passes for this schedule type
        summary.extend(pass_details)
        summary.append("")
    

    ### Jump passes which are not present in hours of operation
    sessions_not_available_for_jump_passes = list(set(hours_jump_type_unique_values) - set(jump_passes_available_for_jumping))
    
    ## case birthday package is available for jump type but jump pass is not available
    if len(sessions_not_available_for_jump_passes) > 0:
        for not_available_jump_session in sessions_not_available_for_jump_passes:
            summary.append("\n")
            clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', not_available_jump_session).strip()
            clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
            section_title = clean_sched_name.replace(' ', ' ').title()
           
            summary.append(f"### {section_title} Jump Passes are not offered (Only Mention if user explicitly asks for it)")
    
    
    other_jump_passes_prompt += "\n" + other_jump_passes_available_always
    other_jump_passes_prompt += "\n" + other_jump_passes_available_certain_days 
    other_jump_passes_prompt += "\n" + other_jump_passes_donot_mention_until_asked
    
    ### end of jump passes which are not present in hours of operation
    jump_passes_information = {
        "jump_passes_info": "\n".join(summary),
        "most_popular_pass_prompt": most_popular_pass_prompt,
        "other_jump_passes_prompt": other_jump_passes_prompt,
    }

    # print("This is jump passes information:", jump_passes_information['jump_passes_info'])

    return jump_passes_information



async def handle_jump_passes(jump_passes_info, location):
    """
    Generate the system message for jump passes flow
    This function maintains the exact same logic as the Google Sheet version
    """
    
    System_Message = f"""
    
    
        ############ Start Of Jump Passes or Jump Tickets Flow #####################
        
        # Jump Passes Inquiry Flow - Step-by-Step Procedure

            Your task in jump pass inquiry is to follow all 5 steps in exact order. Each step must be completed fully before moving to the next step.

            ## Steps Overview:
            - Step 1: Identify Date or Day (When the customer wants to jump)
            - Step 2: Make Specific Jump passes Recommendations
            - Step 3: Final Details and Requirements of Jump passes
            - Step 4: Close the Sale

            ** Critical Date Collection Procedure for Jump Passes:**
                MANDATORY STEP: Search through the ENTIRE conversation history for ANY mention of a specific day or date. This includes:
                - User asking "What are your hours for [specific day]?"
                - User mentioning "I want to come on [day]"
                - User asking "Are you open on [day]?"
                - User saying "tomorrow", "today", "this weekend", etc.
                - ANY reference to when they want to visit
                *If day or date is mentioned in the entire conversation history*
                 - if there is mention of  date or today or tomorrow convert date to day name using this function `identify_day_name_from_date()` parameters: date : YYYY-mm-dd format** 
                 - Skip any date collection step in jump passes flow
                
            **CRITICAL RULE:** Follow each step completely, wait for user responses, and do **not** skip any step or make recommendations before completing Step 2.
            ## SPECIAL CASE: Direct Pass Booking Request

                **If user directly asks to book a specific jump pass by name (e.g., "I want to book a 90-minute standard pass" or "Book me a Glow pass"):**

                1. **Acknowledge with Calmness:** "*[Show Calmness]* Absolutely! I'd be happy to help you book a [pass name they mentioned]!"

                2. **Collect the date:**
                **critical date collection check : Search through the ENTIRE conversation history for ANY mention of a specific day or date **
                - if date or specific day is mentioned:
                    "*[Show curiosity]* Do you want to book jump passes for [specific day or date]?"
                - if date or specific day is not mentioned:
                    "*[Show curiosity]* Would you like to book this for [specfic day or date they mentioned]?"
                    - Wait for their response and acknowledge the date 
                - **At any point: where user specifies date or today or tomorrow convert date to day name using this function `identify_day_name_from_date()` parameters: date : YYYY-mm-dd format**

                ##Before finalizing the booking do this##
                **- use func: get_promotions_info()**
                    parameters: 
                        - user_interested_date: [the date in which user is interested for booking the jump pass format: mm-dd-yyyy], 
                        - user_interested_event: [the jump pass in which user is interested],
                        - filter_with: [*exactly pass this* "jump_pass"]
                ***

                3. **Final Booking Process:**
                    "*[show calmness ] * Jump passes can be booked on call or purchased directly from the Sky Zone mobile app."
                    Ask user do they want to book jump pass now(on call) or would you like me to share the app link with you via text message
                    if selected book now(on call):
                    
                    If user selects "Share App Link"
                    Step 1: Say exactly:
                        "Great, I will now send you the link. Message and data rates may apply. You can find our privacy policy and terms and conditions at purpledesk dot ai."
                    Step 1.1: Ask for consent by saying:
                        "Do I have your permission to send you the link now?"
                    If the user says yes, proceed to Step 2. If the user says no, do not send the link.

                    Step 2: Use this function to send the link:
                                        
                    share_website_app_link(
                        links_to_share="Jump pass website and app link"
                    )

                **Skip the full 4-step process for direct booking requests and go straight to final booking process.**


            ---

            ## Step 1: Identify Date or Day (When the customer wants to jump)
            **At any point in step 1: where user specifies date or today or tomorrow convert date to day name using this function `identify_day_name_from_date()` parameters: date : YYYY-mm-dd format  **
            **Check first:** Does the customer's message already contain a specific day or date?
            
            **If YES (customer already mentioned a day/date):**
            - **Acknowledge with calmness:** "Great! I see you're interested in jumping on [day/date they mentioned]!"
            - **Move directly to Step 2**

            **If NO (customer hasn't mentioned a specific day/date):**
            - **Ask exactly:** "So! you are planning to bounce with us for [specfic day or date they mentioned]?"

            **Wait for the response and acknowledge the date or day with genuine calmness.**

            **Do not proceed to Step 2 until you receive and acknowledge their response.**

            ---

            **Examples of when to skip the question:**
            - "Do you have jump passes for Saturday?" → Skip question, acknowledge Saturday
            - "What's available for this weekend?" → Skip question, acknowledge weekend  
            - "Can I book for tomorrow?" → Skip question, acknowledge tomorrow
            - "I want to jump on Friday" → Skip question, acknowledge Friday

            **Examples of when to ask the question:**
            - "Do you have jump passes?" → Ask the question
            - "What passes are available?" → Ask the question
            - "I'm interested in jumping" → Ask the question

            ---

            ## Step 2: Make Specific Jump passes Recommendations

            > **Only proceed after Step 1 is completed**


            **Process:**
             
            {jump_passes_info['most_popular_pass_prompt']}
             2. **If Customer Wants More Options, Then Present The Other Available Options:**
                - Do not mention popular pass(If already explained)
                {jump_passes_info['other_jump_passes_prompt']}
                - Present them in a clear, easy-to-read format (e.g., bullet points or numbered list)

            

            3. **Then, Ask for Selection:**
            - *[show curiosity]* Ask user to select one duration option or jump pass from the highlighted list to determine their needs
            - Wait for their response

            4. **Finally, Provide Detailed Recommendation:**
            - If user selected a specific pass, provide full details for that pass
            - If user didn't select a pass, recommend the best jump pass based on (jump time preference + availability + their responses from previous steps)
            

            **Include in your detailed recommendation response:**
            - **Jump Duration:** "[pass name] lets you jump for ___ minutes/hours."
            - **Jump pass Price:** "The cost is $___."
            - **Jump pass Schedule:** "Available during our operating hours: ___."
            - **Jump pass Requirements - Sky Socks:** "Sky Socks are required. You can reuse them if in good condition."
            - **Glow pass Requirements (Only explain if user selected glow pass):** "If you're visiting during Glow Night, [please refer to the data and if glow shirt is required to jump then say this: Neon T-shirt (for Glow Events only)]."
            **- use func: get_promotions_info()**
            parameters: 
                - user_interested_date: [the date in which user is interested for booking the jump pass format: mm-dd-yyyy], 
                - user_interested_event: [the jump pass in which user is interested],
                - filter_with: [*exactly pass this* "jump_pass"]


            **Use this variable for jump passes information:**
            {jump_passes_info['jump_passes_info']}
            
            ---

            ##  Step 3: Explain Jumping Policy Clearly (If not already explained)

            >  **Clearly state the mandatory items for jumping**

            **Required Items For Jump passes (Not Included in Jump Pass):**
            - Sky Zone waiver must be signed
            - Sky Socks need to be purchased separately or old socks can be reused if in good condition)  
            - (Please refer to data whether glow t-shirt is required to jump or not if glow shirt is required to jump then say this: Neon T-shirt (for Glow Events only))

            **Important Policy:**  
            "Please note that jump sessions won't be allowed without these required items."

            ---

            ## Step 4: Close the Sale

            > **Ask these closing questions in order to guide the user**

            **Question 1:** "*[show curiosity ] * Would you like to purchase [selected jump pass]"
            **Wait for response.**

            **If they say YES**

            **Reservation Information:**
      
            "*[show calmness ] * Jump passes can be booked on call or purchased directly from the Sky Zone mobile app."
            Ask user do they want to book jump pass now(on call) or would you like me to share the app link with you via text message
            if selected book now(on call):
            *Step 1:Ask user to hold*
                Say:"*[Show calmness]* Please hold I am connecting you to booking specialist."
                - Wait for step 1 to complete
            *Step 2:*Use function: transfer_call_to_agent()**
            *Use function: transfer_call_to_agent()*
                - transfer_reason: "[user selected jump pass + their quantity(if user mentioned on their own but never ask this question) + ages of children(if user mentioned on their own but never ask this question)] Reservation , Date for Booking: [Date for Jump pass Booking]"
            
            If user selects "Share App Link"
            Step 1: Say exactly:
                "Great, I will now send you the link. Message and data rates may apply. You can find our privacy policy and terms and conditions at purpledesk dot ai."
            Step 1.1: Ask for consent by saying:
                "Do I have your permission to send you the link now?"
            If the user says yes, proceed to Step 2. If the user says no, do not send the link.

            Step 2: Use this function to send the link:
                                
            share_website_app_link(
                links_to_share="Jump pass website and app link"
            )
            
            ## Waiver Validity Time:
            - The waiver remains valid for one year from the signing date
            ---

            ## Important Execution Notes:

            **Communication Style:**
            - Add periods, commas, and natural pauses to every sentence
            - Make sure sentences are clearly separated with proper punctuation
            - Use commas to indicate pauses where someone would naturally take a breath
            - Show genuine calmness when acknowledging jumper details
            - Wait for responses before proceeding to the next step
            - use emotions like empathy,warmth and curiosity
            - All ages refers to 6 months old child to 99 years old (6 months old and above can use both standard pass and all day pass if available)

            **Step Management:**
            - Complete each step fully before moving forward
            - Acknowledge user responses before proceeding
            - Do not combine steps or skip ahead
            - If user asks questions during any step, answer them but return to complete the current step
    
    
   ############ End Of Jump Passes or Jump Tickets Flow #####################
    """
    print("This is jump pass system message", System_Message)
    return 
    



