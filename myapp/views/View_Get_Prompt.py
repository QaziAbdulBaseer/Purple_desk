

# # hi, I want you make a new table in th database ( Memebership).

# # The Membership table should have the following columns: 
#     # Location_id (fk to Locations table)
#     # Membership_id (PK , auto increment)
#     # title (STRING , NOT NULL)
#     # schedule_with (ANY TYPE OF ARRAY , nOT NULL)
#     # pitch_priority ( INTEGER , NOT NULL)
#     # pitch_introduction (STRING )
#     # activity_time (STRING )
#     # features (STRING )
#     # valid_until (DATE)
#     # party_discount (DECIMAL)
#     # price (DECIMAL , NOT NULL)
#     # parent_addon_price (DECIMAL)
#     # Subscription  string
#     # tax_included (BOOLEAN , NOT NULL)


# # Then I want you write the CRUD operations for this memberships
# # I am working in djanjo framwork with postgresql database.
# # I also give you some reference code from my existing Jump Pass table and its CRUD operations. for your better understanding.
# # and you also have to write the code in the same way as my existing code.
# # and you also have to write the postman request for testing the CRUD operations.


# # In View_Get_Prompt.py
# from myapp.views.Get_prompt.Get_hours_of_operation import get_hours_of_operation_info
# from myapp.views.Get_prompt.Get_jump_pass import get_jump_pass_info
# from django.http import JsonResponse
# from asgiref.sync import sync_to_async

# async def get_prompt(request, location_id):
#     try:
#         # ... your existing code ...
        
#         # Get timezone (you'll need to get this from your location model)
#         timezone = "Asia/Karachi"

#         # Get both hours of operation and jump pass info
#         hours_of_operation_info = await get_hours_of_operation_info(location_id, timezone)
#         jump_pass_info = await get_jump_pass_info(location_id, timezone)

#         # print("Hours of Operation Info:", hours_of_operation_info)
#         # print("jump_pass_info Info:", jump_pass_info['jump_passes_info'])

#         # Combine both pieces of information
#         combined_prompt = f"""
#             Hours of Operation Info:
#             {hours_of_operation_info}

#             Jump Pass Info:
#             {jump_pass_info['jump_passes_info']}
#         """

#         print("This is combined prompt:", combined_prompt)
        
#         return JsonResponse({
#             "prompt": combined_prompt,
#             "hours_info": hours_of_operation_info,
#             "jump_pass_info": jump_pass_info['jump_passes_info']
#         }, status=200)

#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)










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







        