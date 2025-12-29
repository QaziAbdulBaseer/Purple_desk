

# hi, see now i want you to create differet apis

# like i want i have 1 api what just create a birthday party package prompt and create its markdown file
# same an other api that just create jump pass prompt and create its markdown file
# same for membership
# same for hours of operation
# same for rental facility  mean for every section create a different api that just create that section prompt and save it to markdown file


# but that all files should be saved in same folder that folder name contain the (location id , location name and current date time when the foler or file is created)
# and then in every folder there should be different markdown file for every section prompt
# like birthday party package prompt should be saved in birthday_party_package_prompt.md
# jump pass prompt should be saved in jump_pass_prompt.md
# membership prompt should be saved in membership_prompt.md
# hours of operation prompt should be saved in hours_of_operation_prompt.md  for every one


# then i want you create an other api that will just reture the all the prompt in one markdown file that contain all the section prompt in one file and that file should be saved in the same folder as above  but that api will not save any file its jsut return that file and prompt data 


# and there is one more api will will create all the files and folder in once for give locatoin id. 



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
from myapp.views.Get_prompt.Get_prompt_variables import Get_prompt_variables
from myapp.views.Get_prompt.Get_current_date_and_time import get_current_date_by_location , get_current_time_by_location
from django.http import JsonResponse
from django.conf import settings


async def get_prompt(request, location_id, search_number , client_id):
    try:
        print("Starting get_prompt for location_id:", location_id)
        print("search_number:", search_number)
        print("client_id:", client_id)


        timezone = "Asia/Karachi"\
        # Fetch prompt variables
        prompt_variables = await Get_prompt_variables(location_id)
        print("prompt_variables done")

        current_date = await get_current_date_by_location(location_id)  # "2025-12-15"
        print("get_current_date_by_location done")
        current_time = await get_current_time_by_location(location_id)  # "14:37:05"
        print("get_current_time_by_location done")

        print("starting_guidelines_test done")

        # Fetch all info
        hours_of_operation_info = await get_hours_of_operation_info(location_id, timezone)
        print("hours_of_operation_info done" )

        starting_guidelines_tests = await starting_guidelines_test()
        print("starting_guidelines_test done")
        
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
        
        birthday_party_packages_info  = await load_birthday_party_flow_prompt(location_id, timezone, search_number , client_id)
        # print("This is import to seeeee =-= " , birthday_party_packages_info['customer_information'])
        print("birthday_party_packages_info done")

        current_time_informations = await current_time_information(timezone)
        print("current_time_informations done")

        create_location_info_prompts = await create_location_info_prompt(location_id)
        # Combined prompt with the complete jump pass flow
        combined_prompt = f"""
{starting_guidelines_tests}
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
            "birthday_party_packages_prompt": combined_prompt,
            "promotions_dict": {},
            "prompt_variables": prompt_variables,
            "current_date": current_date,
            "current_time": current_time,
            "customer_information": birthday_party_packages_info['customer_information'],
            # "hours_info": hours_of_operation_info,
            # "jump_pass_flow_prompt": jump_pass_flow_prompt,
            # "jump_pass_info": jump_pass_info.get('jump_passes_info', {}),
            # "membership_flow_prompt": membership_flow_prompt,
            # "membership_info": membership_info.get('memberships_info', {}),
            # "faqs_info": faqs_info,
            # "policies_info": policies_info['formatted_policies'],
            # "rental_facility_info": rental_facility_info['formatted_prompt'],
            # "birthday_party_packages_info": birthday_party_packages_info['system_message'],
            "markdown_file_url": markdown_file_url,
            "markdown_filename": filename
        }, status=200)



    except Exception as e:
        print("Error in get_prompt:", str(e))
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)


