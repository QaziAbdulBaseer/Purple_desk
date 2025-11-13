

from myapp.views.Get_prompt.Get_hours_of_operation import get_hours_of_operation_info
from myapp.views.Get_prompt.Get_jump_pass import get_jump_pass_info
from myapp.views.Get_prompt.Get_membership import get_membership_info  # NEW IMPORT
from django.http import JsonResponse
from asgiref.sync import sync_to_async

async def get_prompt(request, location_id):
    try:
        # ... your existing code ...
        
        # Get timezone (you'll need to get this from your location model)
        timezone = "Asia/Karachi"

        # Get hours of operation, jump pass info, and membership info
        hours_of_operation_info = await get_hours_of_operation_info(location_id, timezone)
        jump_pass_info = await get_jump_pass_info(location_id, timezone)
        membership_info = await get_membership_info(location_id, timezone)  # NEW: Get membership info

        # print("Hours of Operation Info:", hours_of_operation_info)
        # print("jump_pass_info Info:", jump_pass_info['jump_passes_info'])
        print("membership_info Info:", membership_info['memberships_info'])  # NEW: Print membership info

        # Combine all pieces of information
        combined_prompt = f"""
            Hours of Operation Info:
            {hours_of_operation_info}

            Jump Pass Info:
            {jump_pass_info['jump_passes_info']}

            Membership Info:
            {membership_info['memberships_info']}
        """

        # print("This is combined prompt:", combined_prompt)
        
        return JsonResponse({
            "prompt": combined_prompt,
            "hours_info": hours_of_operation_info,
            "jump_pass_info": jump_pass_info['jump_passes_info'],
            "membership_info": membership_info['memberships_info']  # NEW: Include membership info in response
        }, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)







        