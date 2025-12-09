
import os
from datetime import datetime
from myapp.views.Get_prompt.Get_hours_of_operation import get_hours_of_operation_info
from myapp.views.Get_prompt.Get_jump_pass import get_jump_pass_info
from myapp.views.Get_prompt.Get_membership import get_membership_flow_prompt
from myapp.views.Get_prompt.Get_membership import get_membership_info
from myapp.views.Get_prompt.Get_jump_pass import get_jump_pass_flow_prompt
from myapp.views.Get_prompt.Get_FAQs import extract_faqs_for_llm
from myapp.views.Get_prompt.Get_policy import get_policies_for_llm
from myapp.views.Get_prompt.Get_RentalFacility import get_rental_facility_info
from myapp.views.Get_prompt.Get_Birthday_party_packages import load_birthday_party_flow_prompt
from myapp.views.Get_prompt.Get_Static_text_functions import starting_guidelines_test
from myapp.views.Get_prompt.Get_Static_text_functions import current_time_information
from myapp.views.Get_prompt.Get_location_and_available_items import create_location_info_prompt
from django.http import JsonResponse
from django.conf import settings

async def get_prompt(request, location_id):
    try:
        timezone = "Asia/Karachi"
        print("this is 1")

        starting_guidelines_tests = await starting_guidelines_test()
        print("starting_guidelines_test done")

        # Fetch all info
        hours_of_operation_info = await get_hours_of_operation_info(location_id, timezone)
        print("hours_of_operation_info done" )
        
        # Use the new function to get complete jump pass flowmost_popular_pass_prompt
        jump_pass_flow_prompt = await get_jump_pass_flow_prompt(location_id, timezone)
        print("jump_pass_flow_prompt done")
        
        # Still get jump pass info for other uses if needed
        jump_pass_info = await get_jump_pass_info(location_id, timezone)
        print("jump_pass_info done")
        
        membership_flow_prompt = await get_membership_flow_prompt(location_id, timezone)
        print("membership_flow_prompt done")
        
        membership_info = await get_membership_info(location_id, timezone)
        print("membership_info done")   
        
        faqs_info = await extract_faqs_for_llm(location_id)
        print("faqs_info done")
        
        policies_info = await get_policies_for_llm(location_id)
        print("policies_info done")
        
        rental_facility_info = await get_rental_facility_info(location_id, "yes")
        print("rental_facility_info done")
        
        birthday_party_packages_info = await load_birthday_party_flow_prompt(location_id, timezone)
        print("birthday_party_packages_info done")

        current_time_informations = await current_time_information(timezone)
        print("current_time_informations done")

        create_location_info_prompts = await create_location_info_prompt(location_id)
        # Combined prompt with the complete jump pass flow
        combined_prompt = f"""

# start 1

{starting_guidelines_tests}

# start 2

## Call Context
{current_time_informations}

## Birthday Party Packages
{birthday_party_packages_info['system_message']}


## Start Of Memberships Flow
{membership_flow_prompt}

## end Of Memberships Flow

## Start Of Jump Passes Flow
{jump_pass_flow_prompt}
## end Of Jump Passes Flow

## Hours of Operation
{hours_of_operation_info}

## Location

{create_location_info_prompts['location_prompt']}


## FAQs
{faqs_info}

## Policies
{policies_info['formatted_policies']}

## Rental Facilities
{rental_facility_info['formatted_prompt']}


"""

        # Save to markdown file
        filename = f"prompt_{location_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        save_path = os.path.join("generated_md", filename)
        os.makedirs("generated_md", exist_ok=True)

        markdown_file_url = request.build_absolute_uri(f'{settings.MEDIA_URL}{filename}')

        with open(save_path, "w", encoding="utf-8") as f:
            f.write(combined_prompt)
        return JsonResponse({
            "prompt": combined_prompt,
            "hours_info": hours_of_operation_info,
            "jump_pass_flow_prompt": jump_pass_flow_prompt,
            # "jump_pass_info": jump_pass_info['jump_passes_info'] if jump_pass_info['jump_passes_info'] else {},
            "jump_pass_info": jump_pass_info.get('jump_passes_info', {}),

            "membership_flow_prompt": membership_flow_prompt,
            # "membership_info": membership_info['memberships_info'],
            "membership_info": membership_info.get('memberships_info', {}),
            "faqs_info": faqs_info,
            "policies_info": policies_info['formatted_policies'],
            "rental_facility_info": rental_facility_info['formatted_prompt'],
            "birthday_party_packages_info": birthday_party_packages_info['system_message'],
            # "markdown_file_path": save_path
            "markdown_file_url": markdown_file_url,
            "markdown_filename": filename
        }, status=200)



    except Exception as e:
        print("Error in get_prompt:", str(e))
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


