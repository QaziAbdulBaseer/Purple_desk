

import os
from datetime import datetime
from myapp.views.Get_prompt.Get_hours_of_operation import get_hours_of_operation_info
from myapp.views.Get_prompt.Get_jump_pass import get_jump_pass_info
from myapp.views.Get_prompt.Get_membership import get_membership_info
from myapp.views.Get_prompt.Get_FAQs import extract_faqs_for_llm
from myapp.views.Get_prompt.Get_policy import get_policies_for_llm
from myapp.views.Get_prompt.Get_RentalFacility import get_rental_facility_info
from myapp.views.Get_prompt.Get_Birthday_party_packages import load_birthday_party_flow_prompt
from django.http import JsonResponse

async def get_prompt(request, location_id):
    try:
        timezone = "Asia/Karachi"

        # Fetch all info
        hours_of_operation_info = await get_hours_of_operation_info(location_id, timezone)
        print("hours_of_operation_info done")
        jump_pass_info = await get_jump_pass_info(location_id, timezone)
        print("jump_pass_info done")
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

        print("birthday_party_packages info keys:", birthday_party_packages_info.keys())

        combined_prompt = f"""
# Location Prompt Summary

## Hours of Operation
{hours_of_operation_info}

## Jump Passes
{jump_pass_info['jump_passes_info']}

## Memberships
{membership_info['memberships_info']}


## FAQs
{faqs_info}


## Policies
{policies_info['formatted_policies']}

## Rental Facilities
{rental_facility_info['formatted_prompt']}


## Birthday Party Packages
{birthday_party_packages_info['system_message']}
"""

        # -----------------------------
        # SAVE TO MARKDOWN FILE
        # -----------------------------
        filename = f"prompt_{location_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        save_path = os.path.join("generated_md", filename)

        # Ensure directory exists
        os.makedirs("generated_md", exist_ok=True)

        # Write the file
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(combined_prompt)

        # JSON Response
        return JsonResponse({
            "prompt": combined_prompt,
            "hours_info": hours_of_operation_info,
            "jump_pass_info": jump_pass_info['jump_passes_info'],
            "membership_info": membership_info['memberships_info'],
            "faqs_info": faqs_info,
            "policies_info": policies_info['formatted_policies'],
            "rental_facility_info": rental_facility_info['formatted_prompt'],
            "birthday_party_packages_info": birthday_party_packages_info['system_message'],
            "markdown_file_path": save_path  # return path
        }, status=200)

    except Exception as e:
        print("Error in get_prompt:", str(e))
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": str(e)}, status=500)