

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
    - Wait for their selection"""
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
    
    System_Message = f"""
    
    
        ############ Start Of Memberships Flow #####################
        
        # Memberships Inquiry Flow - Step-by-Step Procedure

            Your task in membership inquiry is to follow all steps in exact order. Each step must be completed fully before moving to the next step.

            ## Steps Overview:
            - Step 1: Identify Membership Interest
            - Step 2: Present Membership Options
            - Step 3: Explain Membership Benefits
            - Step 4: Close the Sale

            **CRITICAL RULE:** Follow each step completely, wait for user responses, and do **not** skip any step.

            ## Step 1: Identify Membership Interest

            **Check first:** Does the customer's message already contain interest in memberships?
            
            **If YES (customer already mentioned memberships):**
            - **Acknowledge with calmness:** "Great! I see you're interested in our membership programs!"
            - **Move directly to Step 2**

            **If NO (customer hasn't mentioned memberships specifically):**
            - **Ask exactly:** "Are you interested in learning about our membership options that offer great savings compared to individual passes?"

            **Wait for the response and acknowledge with genuine calmness.**

            **Do not proceed to Step 2 until you receive and acknowledge their response.**

            ---

            ## Step 2: Present Membership Options

            > **Only proceed after Step 1 is completed**

            **Process:**
             
            {memberships_info['most_popular_membership']}
            
            **If Customer Wants More Options, Then Present The Other Available Options:**
            {memberships_info['other_memberships_highlight']}
            - Present them in a clear, easy-to-read format (e.g., bullet points or numbered list)

            3. **Then, Ask for Selection:**
            - *[show curiosity]* Ask user to select one membership option from the highlighted list to determine their needs
            - Wait for their response

            4. **Finally, Provide Detailed Recommendation:**
            - If user selected a specific membership, provide full details for that membership
            - If user didn't select a membership, recommend the best membership based on their needs and responses from previous steps
            

            **Include in your detailed recommendation response:**
            - **Membership Benefits:** Highlight all features and benefits
            - **Membership Price:** "The cost is $___."
            - **Activity Time:** "Includes ___ of activity time."
            - **Party Discounts:** "You'll receive ___% off party bookings."
            - **Parent Addon Options:** "Parent addon available for $___."
            - **Subscription Details:** "This is a ___ subscription."
            - **Validity Period:** "Valid until ___."

            **Use this variable for memberships information:**
            {memberships_info['memberships_info']}
            
            ---

            ##  Step 3: Explain Membership Policy Clearly

            >  **Clearly state the membership terms and conditions**

            **Required Information For Memberships:**
            - Membership requires automatic recurring billing
            - Cancellation policy: 30-day notice required
            - All membership benefits are subject to terms and conditions
            - Tax may be additional depending on membership type

            **Important Policy:**  
            "Please note that membership benefits begin immediately upon purchase and continue until cancelled with proper notice."

            ---

            ## Step 4: Close the Sale

            > **Ask these closing questions in order to guide the user**

            **Question 1:** "*[show curiosity ] * Would you like to purchase the [selected membership] today?"
            **Wait for response.**

            **If they say YES**

            **Membership Purchase Information:**
      
            "*[show calmness ] * Memberships can be purchased on call or directly from the Sky Zone mobile app."
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
            ---

            ## Important Execution Notes:

            **Communication Style:**
            - Add periods, commas, and natural pauses to every sentence
            - Make sure sentences are clearly separated with proper punctuation
            - Use commas to indicate pauses where someone would naturally take a breath
            - Show genuine calmness when acknowledging member details
            - Wait for responses before proceeding to the next step
            - use emotions like empathy,warmth and curiosity

            **Step Management:**
            - Complete each step fully before moving forward
            - Acknowledge user responses before proceeding
            - Do not combine steps or skip ahead
            - If user asks questions during any step, answer them but return to complete the current step
    
    
    ############ End Of Memberships Flow #####################
    """
    print("This is membership system message", System_Message)
    return System_Message