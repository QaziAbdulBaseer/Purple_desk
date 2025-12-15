



import pandas as pd
import re
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Dict, List, Any
from myapp.model.membership_model import Membership
from myapp.model.hours_of_operations_model import HoursOfOperation
from myapp.model.locations_model import Location
from asgiref.sync import sync_to_async
import json

async def get_membership_info(location_id: int, timezone: str) -> dict:
    """
    Main function to get formatted membership information from database
    Returns the same structure as the Google Sheet version
    """
    
    # Fetch memberships from database
    memberships = await sync_to_async(list)(
        Membership.objects.filter(location_id=location_id).order_by('pitch_priority')
    )
    
    # Fetch hours of operation from database
    hours_of_operation = await sync_to_async(list)(
        HoursOfOperation.objects.filter(location_id=location_id)
    )
    
    # Fetch location name
    location = await sync_to_async(Location.objects.get)(location_id=location_id)
    
    # Convert to DataFrames to maintain compatibility with existing code
    membership_data = []
    for membership_obj in memberships:
        # Handle schedule_with field - convert list to string for DataFrame compatibility
        schedule_with = membership_obj.schedule_with
        if isinstance(schedule_with, list):
            schedule_with_str = ",".join(schedule_with)
        else:
            schedule_with_str = str(schedule_with) if schedule_with else ""
            
        membership_data.append({
            'title': membership_obj.title,
            'schedule_with': schedule_with_str,  # Convert list to string
            'pitch_priority': membership_obj.pitch_priority,
            'pitch_introduction': membership_obj.pitch_introduction or "",
            'activity_time': membership_obj.activity_time or "",
            'features': membership_obj.features or "",
            'valid_until': membership_obj.valid_until or "",
            'party_discount': float(membership_obj.party_discount) if membership_obj.party_discount else "",
            'price': float(membership_obj.price),
            'parent_addon_price': membership_obj.parent_addon_price if membership_obj.parent_addon_price else "",
            'Subscription': membership_obj.subscription or "",
            'tax_included': membership_obj.tax_included,
            'Location': location.location_name  # Add location for compatibility
        })
    
    hours_data = []
    for hour_obj in hours_of_operation:
        hours_data.append({
            'jump_type': hour_obj.schedule_with
        })
    
    # Create DataFrames
    df = pd.DataFrame(membership_data)
    if df.empty:
        return {"status": "No data available"}
    hours_df = pd.DataFrame(hours_data)
    
    # Use the existing function with the DataFrames
    schedule_with_dict = {}  # This was in original code but not used, keeping for compatibility
    
    result = await membership_info(df, schedule_with_dict)
    
    # Add formatted display using the new function
    structured_data = await get_structured_membership_data(location_id, timezone)
    formatted_display = await format_memberships_for_display(structured_data, location.location_name)
    
    # Add to result
    result['formatted_display'] = formatted_display
    result['structured_data'] = structured_data
    
    return result


async def get_structured_membership_data(location_id: int, timezone: str) -> Dict[str, Any]:
    """
    Get structured membership data for formatting
    """
    # Fetch memberships from database
    memberships = await sync_to_async(list)(
        Membership.objects.filter(location_id=location_id).order_by('pitch_priority')
    )
    
    # Organize data by schedule type and priority
    structured_data = {
        "total_memberships": len(memberships),
        "most_popular_membership": None,
        "memberships_by_schedule": {},
        "other_available_memberships": [],
        "do_not_pitch_memberships": [],
        "unavailable_schedules": []
    }
    
    # Get all unique schedule types from memberships
    all_schedule_types = set()
    for membership_obj in memberships:
        schedule_with = membership_obj.schedule_with
        if isinstance(schedule_with, list):
            for schedule in schedule_with:
                if schedule and schedule != 'closed':
                    all_schedule_types.add(schedule)
        elif schedule_with and schedule_with != 'closed':
            all_schedule_types.add(schedule_with)
    
    # Initialize memberships_by_schedule structure
    for schedule_type in all_schedule_types:
        structured_data["memberships_by_schedule"][schedule_type] = []
    
    # Process each membership
    for membership_obj in memberships:
        membership_data = {
            "title": membership_obj.title,
            "pitch_introduction": membership_obj.pitch_introduction or "",
            "activity_time": membership_obj.activity_time or "",
            "features": membership_obj.features or "",
            "valid_until": membership_obj.valid_until or "",
            "party_discount": str(membership_obj.party_discount) if membership_obj.party_discount else "",
            "price": str(membership_obj.price),
            "parent_addon_price": str(membership_obj.parent_addon_price) if membership_obj.parent_addon_price else "",
            "subscription": membership_obj.subscription or "",
            "tax_included": membership_obj.tax_included,
            "pitch_priority": membership_obj.pitch_priority
        }
        
        # Categorize by priority
        if membership_obj.pitch_priority == 1:
            structured_data["most_popular_membership"] = membership_data
        elif membership_obj.pitch_priority == 999:
            structured_data["do_not_pitch_memberships"].append(membership_data)
        else:
            structured_data["other_available_memberships"].append(membership_data)
        
        # Add to schedule types
        schedule_with = membership_obj.schedule_with
        if isinstance(schedule_with, list):
            for schedule in schedule_with:
                if schedule and schedule != 'closed' and schedule in structured_data["memberships_by_schedule"]:
                    structured_data["memberships_by_schedule"][schedule].append(membership_data)
        elif schedule_with and schedule_with != 'closed' and schedule_with in structured_data["memberships_by_schedule"]:
            structured_data["memberships_by_schedule"][schedule_with].append(membership_data)
    
    # Get unavailable schedules (schedules in hours but not in memberships)
    hours_of_operation = await sync_to_async(list)(
        HoursOfOperation.objects.filter(location_id=location_id)
    )
    
    hours_schedule_types = set()
    for hour_obj in hours_of_operation:
        if hour_obj.schedule_with and hour_obj.schedule_with != 'closed':
            hours_schedule_types.add(hour_obj.schedule_with)
    
    structured_data["unavailable_schedules"] = list(hours_schedule_types - all_schedule_types)
    
    return structured_data


async def format_memberships_for_display(membership_data: Dict, location_name: str) -> str:
    """Format the membership data for easy reading - async version"""
    def _format_output():
        output_lines = []
        
        # Current info section
        output_lines.append("=== MEMBERSHIPS INFORMATION ===")
        output_lines.append(f"Location: {location_name}")
        output_lines.append(f"Total Available Memberships: {membership_data['total_memberships']}")
        output_lines.append("")
        
        # Most Popular Membership (Priority 1)
        if membership_data["most_popular_membership"]:
            output_lines.append("=== MOST POPULAR MEMBERSHIP ===")
            popular = membership_data["most_popular_membership"]
            output_lines.append(f"Membership Title: {popular['title']}")
            output_lines.append(f"Pitch Introduction: {popular['pitch_introduction']}")
            output_lines.append(f"Activity Time: {popular['activity_time']}")
            output_lines.append(f"Price: ${popular['price']}")
            if popular['features']:
                output_lines.append(f"Features: {popular['features']}")
            if popular['subscription']:
                output_lines.append(f"Subscription: {popular['subscription']}")
            if popular['party_discount']:
                output_lines.append(f"Party Discount: ${popular['party_discount']}")
            if popular['parent_addon_price']:
                output_lines.append(f"Parent Addon Price: ${popular['parent_addon_price']}")
            if popular['valid_until']:
                output_lines.append(f"Valid Until: {popular['valid_until']}")
            
            if popular['tax_included']:
                output_lines.append(f"Tax Included: Yes")
            else:
                output_lines.append(f"Tax Included: No")
                
            output_lines.append("")
        
        # Memberships by Schedule Type
        output_lines.append("=== MEMBERSHIPS BY SCHEDULE TYPE ===")
        
        for schedule_type, memberships in membership_data["memberships_by_schedule"].items():
            # Format schedule type name
            clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', schedule_type).strip()
            clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
            formatted_schedule_type = clean_sched_name.replace(' ', ' ').title()
            
            output_lines.append(f"\n{formatted_schedule_type}:")
            
            if not memberships:
                output_lines.append("  No memberships available")
                continue
                
            for membership_item in memberships:
                output_lines.append(f"  - {membership_item['title']}")
                output_lines.append(f"    Pitch: {membership_item['pitch_introduction']}")
                output_lines.append(f"    Activity Time: {membership_item['activity_time']}")
                output_lines.append(f"    Price: ${membership_item['price']}")
                
                if membership_item['features']:
                    output_lines.append(f"    Features: {membership_item['features']}")
                if membership_item['subscription']:
                    output_lines.append(f"    Subscription: {membership_item['subscription']}")
                if membership_item['party_discount']:
                    output_lines.append(f"    Party Discount: ${membership_item['party_discount']}")
                if membership_item['parent_addon_price']:
                    output_lines.append(f"    Parent Addon: ${membership_item['parent_addon_price']}")
                if membership_item['valid_until']:
                    output_lines.append(f"    Valid Until: {membership_item['valid_until']}")
                
                if membership_item['tax_included']:
                    output_lines.append(f"    Tax Included: Yes")
                else:
                    output_lines.append(f"    Tax Included: No")
                
                priority_display = "Do not pitch" if membership_item['pitch_priority'] == 999 else membership_item['pitch_priority']
                output_lines.append(f"    Priority: {priority_display}")
        
        # Other Available Memberships (Priority 2-998)
        if membership_data["other_available_memberships"]:
            output_lines.append("\n=== OTHER AVAILABLE MEMBERSHIPS ===")
            for membership_item in membership_data["other_available_memberships"]:
                output_lines.append(f"  - {membership_item['title']}: {membership_item['pitch_introduction']} - ${membership_item['price']}")
        
        # Do Not Pitch Memberships (Priority 999)
        if membership_data["do_not_pitch_memberships"]:
            output_lines.append("\n=== DO NOT PITCH MEMBERSHIPS ===")
            output_lines.append("(Only mention if user explicitly asks for these)")
            for membership_item in membership_data["do_not_pitch_memberships"]:
                output_lines.append(f"  - {membership_item['title']}: {membership_item['pitch_introduction']} - ${membership_item['price']}")
        
        # Unavailable Schedule Types
        if membership_data["unavailable_schedules"]:
            output_lines.append("\n=== UNAVAILABLE SCHEDULE TYPES ===")
            output_lines.append("(No memberships offered for these schedule types)")
            for schedule_type in membership_data["unavailable_schedules"]:
                clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', schedule_type).strip()
                clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
                formatted_schedule_type = clean_sched_name.replace(' ', ' ').title()
                output_lines.append(f"  - {formatted_schedule_type}")
        
        # Summary
        output_lines.append("\n=== SUMMARY ===")
        most_popular_name = membership_data['most_popular_membership']['title'] if membership_data['most_popular_membership'] else 'None'
        output_lines.append(f"Most Popular: {most_popular_name}")
        output_lines.append(f"Total Schedule Types: {len(membership_data['memberships_by_schedule'])}")
        output_lines.append(f"Other Available Memberships: {len(membership_data['other_available_memberships'])}")
        output_lines.append(f"Do Not Pitch Memberships: {len(membership_data['do_not_pitch_memberships'])}")
        output_lines.append(f"Unavailable Schedule Types: {len(membership_data['unavailable_schedules'])}")
        
        return "\n".join(output_lines)
    
    loop = asyncio.get_event_loop()
    with ThreadPoolExecutor() as executor:
        return await loop.run_in_executor(executor, _format_output)


async def membership_info(df: pd.DataFrame, schedule_with_dict: dict) -> dict:
    """
    Process membership information and format it for the prompt
    This function maintains the exact same logic as the Google Sheet version
    """
    summary = []
    location = df['Location'].iloc[0].title()

    most_popular_membership = ""
    most_popular_membership_name = ""
    other_memberships_highlight = ""
    
    summary.append(f"### Membership Information \n")

    for _, row in df.iterrows():
        title = row.get('title',"na")
        title  = title.upper()
        schedule_with = row.get('schedule_with')
        activity_time = row.get('activity_time')
        features = row.get('features')
        valid_until = row.get('valid_until')
        if valid_until=="nan" or pd.isna(valid_until):
            valid_until_sentence = ""
        else:
            valid_until_sentence =f"Membership Valid Until : {valid_until}"
        price = row.get('price')
        parent_addon_price = row.get('parent_addon_price')
        subscription = row.get('Subscription')
        party_discount = row.get('party_discount')
        if party_discount=="nan" or pd.isna(party_discount):
            party_discount_sentence = ""
        else:
            party_discount_sentence =f"Party discounts : {party_discount}"
        pitch_priority = int(row.get('pitch_priority',"999"))
        pitch_introduction = row.get('pitch_introduction')

        most_popular_membership_name = title

        if pitch_priority==1:
            most_popular_membership=f"""
            ### STEP 1: [ALWAYS HIGHLIGHT *{title} - {pitch_introduction}* FIRST]
            - Lead with calmness and warmth about {title}
            - Make natural sentences out of this
            - Provide a SHORT sales highlight focusing ONLY on:
            * Activity time : {activity_time}
            * {party_discount_sentence}
            - DO NOT explain anything else at this stage
            - Use warmth language: "I'm excited to tell you about our incredible {title}!"

            ### STEP 2: ASK FOR INTEREST
            - With warm enthusiasm, ask: "Would you like to learn more about the {title} or hear about other options?"
            - Wait for user response

            ### STEP 3A: IF USER SAYS YES TO {title}:
            - construct natural sentences
            - Explain {title} details with calmness
            - Highlight ALL of the following:
            * Activity time : {activity_time}
            * Features : {features}
            * {party_discount_sentence}
            * Price : {price}
            * Parent addon price: {parent_addon_price}
            * {valid_until_sentence}
            * Subscription: {subscription}

            """
        else:
            if other_memberships_highlight == "":
                other_memberships_highlight = f"*{title} - {pitch_introduction}*"
            else:
                other_memberships_highlight +="," f"*{title} - {pitch_introduction}*"


        # Start composing the pass description
        pass_lines = []

        if isinstance(title, str) and title.strip():
            pass_lines.append(f"**{title.strip()}**")

        # Schedule with values could be comma-separated list, so split and get info for each
        if isinstance(schedule_with, str) and schedule_with.strip():
            schedule_keys = [s.strip() for s in schedule_with.split(',')]
            

        if isinstance(activity_time, str) and activity_time.strip():
            pass_lines.append(f"Activity time: {activity_time.strip()}.")

        if isinstance(features, str) and features.strip():
            # Replace newlines with commas for smoother speech or display
            features_clean = features.replace('\n', ', ')
            pass_lines.append(f"Features: {features_clean}.")

        if isinstance(valid_until, str) and valid_until.strip():
            pass_lines.append(f"{valid_until_sentence.strip()}.")

        if isinstance(price, (int, float)):
            pass_lines.append(f"Price: ${str(price).strip().replace('.', ' point ')}.")

        if isinstance(parent_addon_price, str) and parent_addon_price.strip() and parent_addon_price.lower() != "not_allowed":
            # pass_lines.append(f"Parent add-on price: ${parent_addon_price.strip()}.")
            pass_lines.append(f"Parent add-on price: ${str(parent_addon_price).strip().replace('.',' point ')}.")

        if isinstance(subscription, str) and subscription.strip():
            pass_lines.append(f"Subscription type: {subscription.strip()}.")

        if isinstance(party_discount, str) and party_discount.strip():
            pass_lines.append(f"{party_discount_sentence.strip()}.")

        # Join the pass info with line breaks and add a blank line after each pass
        summary.append("\n".join(pass_lines) + "\n")

    other_memberships_highlight_step = f"""### STEP 3B: IF USER SAYS NO TO {most_popular_membership_name}
    - Share only the names of other available memberships:{other_memberships_highlight} .DO NOT explain anything else at this stage except for names of the memberships
    - Ask with warmth: "Which membership would you like me to explain in detail?"
    - Wait for their selection
    
### STEP 4: Explain Selected Membership
    - Warmly describe:
    - Activity time
    - Features
    - Party discounts (if any)
    - Pricing
    - Parent addon
    - Validity
    - Subscription details"""
    memberships_info_dict = {
        "most_popular_membership":most_popular_membership,
        "other_memberships_highlight" : other_memberships_highlight_step,
        "memberships_info":"\n".join(summary) 
    
    }
    return memberships_info_dict


async def handle_memberships(memberships_info, location):
    """
    Generate the system message for memberships flow
    This function maintains the exact same logic as the Google Sheet version
    """
    
    # Extract the most popular membership steps
    most_popular_section = memberships_info.get('most_popular_membership', '')
    other_memberships_section = memberships_info.get('other_memberships_highlight', '')
    
    # Clean up the sections to get just the step-by-step parts
    # Extract STEP 1, STEP 2, STEP 3A from most_popular_membership
    step1 = ""
    step2 = ""
    step3a = ""
    
    if most_popular_section:
        lines = most_popular_section.split('\n')
        current_step = ""
        step_content = []
        
        for line in lines:
            line_stripped = line.strip()
            if "STEP 1:" in line_stripped:
                current_step = "STEP 1"
                step_content = [line_stripped]
            elif "STEP 2:" in line_stripped:
                current_step = "STEP 2"
                step_content = [line_stripped]
            elif "STEP 3A:" in line_stripped:
                current_step = "STEP 3A"
                step_content = [line_stripped]
            elif current_step and line_stripped:
                step_content.append(line_stripped)
            
            # Store when we hit the next step marker or end
            if current_step == "STEP 1" and ("STEP 2:" in line_stripped or not line_stripped):
                step1 = '\n'.join(step_content)
                step_content = []
            elif current_step == "STEP 2" and ("STEP 3A:" in line_stripped or not line_stripped):
                step2 = '\n'.join(step_content)
                step_content = []
    
    # Extract STEP 3B from other_memberships_highlight
    step3b = other_memberships_section if other_memberships_section else ""
    
    # Format the steps
    formatted_steps = f"""### STEP 1: [ALWAYS HIGHLIGHT MOST POPULAR MEMBERSHIP FIRST]
{step1}

### STEP 2: ASK FOR INTEREST
{step2}

### STEP 3A: IF USER SAYS YES TO MOST POPULAR MEMBERSHIP:
{step3a}

### STEP 3B: IF USER SAYS NO TO MOST POPULAR MEMBERSHIP
{step3b}

### STEP 4: Explain Selected Membership
- Warmly describe:
- Activity time
- Features
- Party discounts (if any)
- Pricing
- Parent addon
- Validity
- Subscription details"""
    
    System_Message = f"""
    
    
        ############ Start Of Memberships Flow #####################
        
        # Memberships Inquiry Flow - Step-by-Step Procedure

            {formatted_steps}

            ## Step 5: Explain Membership Policy Clearly

            >  **Clearly state the membership terms and conditions**

            **Required Information For Memberships:**
            - Membership requires automatic recurring billing
            - Cancellation policy: 30-day notice required
            - All membership benefits are subject to terms and conditions
            - Tax may be additional depending on membership type

            **Important Policy:**  
            "Please note that membership benefits begin immediately upon purchase and continue until cancelled with proper notice."

            ## Step 6: Close the Sale

            > **Ask these closing questions in order to guide the user**

            **Question 1:** "*[show curiosity]* Would you like to purchase the [selected membership] today?"
            **Wait for response.**

            **If they say YES**

            **Membership Purchase Information:**
      
            "*[show calmness]* Memberships can be purchased on call or directly from the Sky Zone mobile app."
            Ask user do they want to purchase membership now(on call) or would you like me to share the app link with you via text message
            
            if selected purchase now(on call):
            *Step 1:Ask user to hold*
                Say:"*[Show calmness]* Please hold I am connecting you to membership specialist."
                - Wait for step 1 to complete
            *Step 2:*Use function: transfer_call_to_agent()**
            *Use function: transfer_call_to_agent()*
                - transfer_reason: "[user selected membership] Membership Purchase"
            
            If user selects "Share App Link"
            Step 1: Say exactly:
                "Great, I will now send you the link. Message and data rates may apply. You can find our privacy policy and terms and conditions at purpledesk dot ai."
            Step 1.1: Ask for consent by saying:
                "Do I have your permission to send you the link now?"
            If the user says yes, proceed to Step 2. If the user says no, do not send the link.

            Step 2: Use this function to send the link:
                                
            share_website_app_link(
                links_to_share="Membership website and app link"
            )
            
            ## Membership Benefits:
            - Unlimited access during operating hours
            - Discounts on additional services
            - Priority booking for popular time slots

            **Communication Style:**
            - Add periods, commas, and natural pauses to every sentence
            - Make sure sentences are clearly separated with proper punctuation
            - Use commas to indicate pauses where someone would naturally take a breath
            - Show genuine calmness when acknowledging member details
            - Wait for responses before proceeding to the next step
            - use emotions like empathy,warmth and curiosity
    
    
    ############ End Of Memberships Flow #####################
    """
    return System_Message




async def get_membership_flow_prompt(location_id: int, timezone: str) -> str:
    """
    Main function to generate complete membership flow prompt
    Returns the formatted membership flow system message
    """
    
    try:
        # Get membership info (includes most_popular_membership, other_memberships_highlight, etc.)
        membership_info_dict = await get_membership_info(location_id, timezone)
        
        # Get location name from the first row or structured data
        location_name = "Unknown Location"
        if 'structured_data' in membership_info_dict:
            # You might need to fetch location name from Location model
            # For now, use the structured data or get it from db
            try:
                location_obj = await sync_to_async(Location.objects.get)(location_id=location_id)
                location_name = location_obj.location_name
            except:
                # Fallback to getting from membership data
                if isinstance(membership_info_dict, dict) and 'memberships_info' in membership_info_dict:
                    # Extract location from membership info if available
                    lines = membership_info_dict['memberships_info'].split('\n')
                    for line in lines:
                        if 'Location:' in line:
                            location_name = line.split('Location:')[1].strip()
                            break
        
        # Generate the membership flow system message using handle_memberships
        system_message = await handle_memberships(membership_info_dict, location_name)
        
        # Extract just the membership flow section (between the ### Start and ### End markers)
        # This ensures we only get the flow part without extra formatting
        start_marker = "############ Start Of Memberships Flow #####################"
        end_marker = "############ End Of Memberships Flow #####################"
        
        # Find the start and end positions
        start_pos = system_message.find(start_marker)
        end_pos = system_message.find(end_marker)
        
        if start_pos != -1 and end_pos != -1:
            # Extract the flow section including the markers
            flow_section = system_message[start_pos:end_pos + len(end_marker)]
            
            # Now format it according to the example prompt provided
            formatted_prompt = f"""### Start Of Memberships Flow ####
*Direct Question Override*
- If the user asks a specific membership question, answer it directly and skip the flow.
**- Promotion Retrieval **
use function: get_promotions_info()
parameters:
user_interested_date = today (mm-dd-yyyy)
user_interested_event = selected membership
filter_with = "memberships"
## STEP-BY-STEP MEMBERSHIP FLOW:

{membership_info_dict.get('most_popular_membership', '')}

{membership_info_dict.get('other_memberships_highlight', '')}

## Step 5:Check Promotions (Mandatory)
- Call get_promotions_info() again using the same parameters before proceeding.

### STEP 6: CLOSING & NEXT STEPS
- Ask: "Would you like to know how to start your membership?"
- If yes tell user:"Memberships can be directly subscribed from the Sky Zone mobile app."
Ask if user wants the link via text.
If user chooses Share App Link:
Step 1 (say exactly):
"Great, I will now send you the link. Message and data rates may apply. You can find our privacy policy and terms and conditions at purpledesk dot ai."
Step 1.1:
"Do I have your permission to send you the link now?"
If yes → Step 2:
share_website_app_link(
links_to_share="Membership subscription Website and App link"
)

## MEMBERSHIP DETAILS TO INCLUDE:
{membership_info_dict.get('memberships_info', '')}

## Sky Socks & Neon Shirt Rules
1. Birthday party → socks included
2. Membership jump sessions → socks required (or reuse if in good condition)
3. Glow sessions → socks + Neon T-shirt if required by data

## Upselling Strategy:
- If the user shows interest in the Basic Membership Package, warmly highlight the amazing benefits of the Elite Membership

## Membership Subscription Process:
1. subscribed using Sky Zone mobile app
2. Use share_website_app_link for sending link
2. Payment:
- monthly auto-renew (credit card)
- Cancellation: 5 business days notice
3. Waiver required (valid for 1 year)

## Membership Cancellation Process:
If user wants to cancel membership:
Say: "To help with membership cancellation,Should I transfer you to a team member."
if user says yes or similar confirmation:
Call function:
transfer_call_to_agent(
transfer_reason="[selected Membership] Cancellation"
)

## Membership Benefits Emphasis:
- Better value than individual jump passes
- Flexible use any operating day
- Access to exclusive member events

*Membership Questions:*
- Cancel anytime (30-day notice)
- No long-term commitment
- Upgrades allowed anytime
- Valid only at {location_name}
- Can freeze for up to 30 days/year

### End Of Memberships Flow ###"""
            
            return formatted_prompt
        
        # If markers not found, return the entire system message
        return system_message
        
    except Exception as e:
        print(f"Error generating membership flow prompt: {str(e)}")
        import traceback
        traceback.print_exc()
        return f"Error generating membership flow: {str(e)}"



