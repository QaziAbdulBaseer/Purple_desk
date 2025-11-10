# OK now i have a code that load the jump pass for the prompt from google sheet and format it accordingly
# But now i have a database and I want to load the jump pass data from database instead of google sheet
# now I give you the gooogle sheet code and database model and the view file that load the data from database
# and you have to write the compleate code line by line and word by line and word that will load the jump pass data from database
# and I want the same type of code that i used for the google sheet data loading and formatting but just want to load data from database

# this is the code that load the jump pass data from google sheet and format it accordingly



async def jump_pass_info(df: pd.DataFrame, schedule_with_dict: dict,hours_df:pd.DataFrame) -> str:
    summary = []
    
    # Get unique schedule_with values
    schedule_with_values = df['schedule_with'].unique()
    hours_jump_type_unique_values = hours_df['jump_type'].unique().tolist() 
    most_popular_pass_prompt = ""
    other_jump_passes_prompt = "### Other Jump pass options"
    other_jump_passes_prompt += "\n Please construct Natural Sentences and only List Passes Names"
    # other_jump_passes_available_always = "*Other Jump Passes options (available always)*"
    # other_jump_passes_available_certain_days = "*Other Jump Passes options (available certain days Please check schedule of hours of operations before mentioning them)*"
    # other_jump_passes_donot_mention_until_asked = "*Other Jump Passes options (Donot mention until explicitly asked Please check schedule of hours of operations to check availability of them)*"
    other_jump_passes_available_always = ""
    other_jump_passes_available_certain_days = ""
    other_jump_passes_donot_mention_until_asked = ""



    ## case birthday package is available for jump type but jump pass is not available
    jump_passes_available_for_jumping = []
    for sched in schedule_with_values:
        df_sched = df[df['schedule_with'] == sched]
        
        # Create clean section header
        schedule_with_list = sched.split(",")
        cleaned_schedule_with_list = []
        for single_schedule_with in schedule_with_list:
            clean_sched_name = re.sub(r'[^a-zA-Z0-9\s]', ' ', single_schedule_with).strip()
            clean_sched_name = re.sub(r'\s+', ' ', clean_sched_name)
            section_title = clean_sched_name.replace(' ', ' ').title()
            section_title = section_title + " Hours (Session)"
            cleaned_schedule_with_list.append(section_title)

            if single_schedule_with not in jump_passes_available_for_jumping:
                jump_passes_available_for_jumping.append(single_schedule_with)
        scheduling_instruction = ""
        if len(schedule_with_list)>1:
            section_title = " and ".join(cleaned_schedule_with_list) 
            # extra_instruction = f"(The below jump pass or jump tickets are available during {len(schedule_with_list)} sessions ( {sched}) hours)"
            scheduling_instruction = f"Schedule Below Jump passes or Jump tickets with {len(schedule_with_list)} sessions {section_title} available in hours of operation for requested date or day - only tell user this pass if available for requested date or day"

        else:
            section_title = "".join(cleaned_schedule_with_list)
            scheduling_instruction = f"""Schedule Below Jump passes or Jump tickets with {sched.replace("_"," ")} available in hours of operation for requested date or day - only tell user this pass if available for requested date or day"""

        summary.append(f"#### {section_title} Jump Passes")
        summary.append(scheduling_instruction)
        summary.append(f"Passes information that schedule with {section_title}:")
        
        summary.append("")
        
        # Group passes by type for better organization
        pass_details = []
        for _, row in df_sched.iterrows():
            pass_name = row['pass_name']
            pass_name_temp = pass_name
            temp_recommendations = row["recommendations"]
            recommendations = ""
            if temp_recommendations.strip() and temp_recommendations.replace(" ",""):
                if pd.notna(temp_recommendations) and str(temp_recommendations)!="nan":
                    recommendations = f"({temp_recommendations})"
                
            starting_day = row["starting_day_name"]
            ending_day = row["ending_day_name"]
            
            starting_day_and_ending_day = ""
            if starting_day and ending_day:
                if starting_day.replace(" ","") and ending_day.replace(" ",""):
                    if (pd.notna(starting_day) and  str(starting_day).lower() != "nan") and  (pd.notna(ending_day) and str(starting_day).lower() != "nan"):
                        starting_day_and_ending_day = f"| Available Days : {starting_day} to {ending_day}"
            # print(f"Pass name {pass_name} - {starting_day_and_ending_day}")
            if recommendations.strip() and recommendations.replace(" ",""):
                if pd.notna(recommendations) and str(recommendations)!="nan":
                    pass_name = f" {pass_name}  {recommendations}   " 
            age = row['age_allowed']
            # start_day = row['starting_day_name'] if pd.notna(row['starting_day_name']) else ""
            # end_day = row['ending_day_name'] if pd.notna(row['ending_day_name']) else ""
            jump_time = row['jump_time_allowed']
            # price = str(row['price']).replace("."," point ")
            price = str(row['price']).strip().replace('.', ' point ')
            introductory_pitch = row["pitch_introduction"]
            priority = row["pitch_priority"]
            availability = row["availability_days"]
            if int(priority)==1:
                most_popular_pass_prompt = f"""1. **[Always Present The {introductory_pitch} {jump_time} {pass_name_temp} for {age} First]:**
                - Calculate the day from selected date
                - Present the {introductory_pitch} {jump_time} {pass_name_temp} {recommendations} for {age} as the primary option:
                    - **Say Exactly:** "For our most popular pass, the {jump_time} {pass_name_temp} for {age}, you get {jump_time} of jump time for $[price of 90-Minute standard pass]."
                    - **Say Exactly Do not change any words:** "We have other jump passes as well - would you like to hear about those options or would you like to purchase the standard pass?"
                    - **Say Exactly Do not change any words:**"Just to let you know, memberships offer big savings compared to buying individual passes."""
                # jump_passes_priority_list.append({
                #     "most_popular_pass":{
                #         "pass_name": f" {jump_time} {pass_name_temp}",
                #         "recommended_for": recommendations if recommendations else "empty",
                #         "starting_day_and_ending_day": starting_day_and_ending_day if starting_day_and_ending_day else "empty",
                #         "ages_allowed": age.lower(),
                #         "jump_time":jump_time,
                #         "price": f"${price}", 

                #     }
                # })
            elif int(priority)==999:
                pass
                # other_jump_passes_donot_mention_until_asked +=f"""\n - Pass Name:{pass_name_temp} (Donot Mention Until User Explicitly asks for {pass_name_temp}) {recommendations} | Introductory Pitch:{introductory_pitch} | jump time:{jump_time} | ages for: {age} """

                # jump_passes_priority_list.append({
                #     int(priority):{
                #         # "pass_name": f" {jump_time} {pass_name_temp} (Donot mention until user explicitly asks for it)",
                #         "pass_name": f"{pass_name_temp} (Donot mention until user explicitly asks for it)",
                #         "recommended_for": recommendations if recommendations else "empty",
                #         "starting_day_and_ending_day": starting_day_and_ending_day if starting_day_and_ending_day else "empty",
                #         # "ages_allowed": age.lower(),
                #         # "jump_time":jump_time,
                #         # "price": f"${price}", 

                #     }
                # })
            else:
                if availability == "always":
                    other_jump_passes_available_always +=f"""\n - Pass Name:{pass_name_temp} {recommendations} | Introductory Pitch:{introductory_pitch} | jump time:{jump_time} | ages for: {age} """
                    # jump_passes_always_available_passes.append(
                    #     {
                    #         int(priority):{
                    #         # "pass_name": f" {jump_time} {pass_name_temp} (Donot mention until user explicitly asks for it)",
                    #         "pass_name": f"{pass_name_temp}",
                    #         "recommended_for": recommendations if recommendations else "empty",
                    #         "starting_day_and_ending_day": starting_day_and_ending_day if starting_day_and_ending_day else "empty",
                    #         # "ages_allowed": age.lower(),
                    #         # "jump_time":jump_time,
                    #         # "price": f"${price}", 

                    #     }
                    #     }
                    # )
                else:
                    other_jump_passes_available_certain_days += f"""\n - Pass Name:{pass_name_temp}( {pass_name_temp} is available on certain days Please check schedule of hours of operations before mentioning {pass_name_temp}) {recommendations} | Introductory Pitch:{introductory_pitch} | jump time:{jump_time} | ages for: {age} """
                    # jump_passes_certain_days_available_passes.append(
                    #     {
                    #     int(priority):{
                    #     # "pass_name": f" {jump_time} {pass_name_temp} (Donot mention until user explicitly asks for it)",
                    #     "pass_name": f"{pass_name_temp} (Only Mention This Pass if {section_title} time session is available for the requested day or day)",
                    #     "recommended_for": recommendations if recommendations else "empty",
                    #     "starting_day_and_ending_day": starting_day_and_ending_day if starting_day_and_ending_day else "empty",
                    #     # "ages_allowed": age.lower(),
                    #     # "jump_time":jump_time,
                    #     # "price": f"${price}", 

                    # }
                    # }
                        
                    #     )

                


            
            if not isinstance(pass_name, str) or pass_name.strip() == "":
                continue
            
            # Format availability
            # availability = ""
            # if start_day and end_day:
            #     availability = f" | Available: {start_day} to {end_day}"
            
            # Create detailed entry
            entry = f"- **{pass_name.strip()}** {starting_day_and_ending_day} | Price : ${price} | Ages Allowed: {age.lower()} | Jump Time: {jump_time}"
            pass_details.append(entry)

        ## sorted keys of always and certain days passes
        # print(f"Jump passes Priority List: { jump_passes_priority_list}")
        # print(f"Always available Jump passes Priority List: { jump_passes_always_available_passes}")  
        # print(f"Jump passes Priority List: { jump_passes_always_available_passes}")


        # jump_passes_priority_list
        # jump_passes_always_available_passes  = []
        # jump_passes_certain_days_available_passes = []
        
        # Add all passes for this schedule type
        summary.extend(pass_details)
        summary.append("")
    

    ### Jump passes which are not present in hours of operation
    sessions_not_available_for_jump_passes  = list(set(hours_jump_type_unique_values)- set(jump_passes_available_for_jumping) )
    
    ## case birthday package is available for jump type but jump pass is not available
    if len(sessions_not_available_for_jump_passes) >0:
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
        "other_jump_passes_prompt" : other_jump_passes_prompt,
    }

      
    return jump_passes_information



async def  handle_jump_passes(jump_passes_info,location):
    
    
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
                    
                    If user selects “Share App Link”
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
            
            If user selects “Share App Link”
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
    
    return System_Message    



# this is the view file and the database model code for your reference


