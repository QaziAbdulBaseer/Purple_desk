





# # ok now i want to modified that code

# # 1 i want for one loacation there is just one folder in the generated prompt folder
# # and that folder contait the location id and location name that it

# # and if we create or call any api then just the specifice api file will update form that folder.


# # and when i call the get combined api then same happend its just (combined all the .md files and return the required file)


# # so in short we have 1 folder for each location. and we just update or create the .md files for the prompts parts like 

# # birthday_party_package_prompt.md
# # combined_all_prompts.md
# # current_date_prompt.md
# # current_time_info_prompt.md
# # current_time_prompt.md
# # faqs_prompt.md
# # hours_of_operation_prompt.md
# # jump_pass_info_prompt.md
# # jump_pass_prompt.md
# # location_info_prompt.md
# # membership_info_prompt.md
# # membership_prompt.md
# # policies_prompt.md
# # prompt_variables.md
# # rental_facility_prompt.md
# # starting_guidelines_prompt.md



# # so the get-combined-all will just mearged all the file and return
# # myapp\views\Individual_Prompts\create_individual_prompts.py

# import os
# from datetime import datetime
# from django.http import JsonResponse
# from django.conf import settings
# from myapp.utils.prompt_file_utils import create_location_folder, save_markdown_file, combine_all_prompts
# from myapp.views.Get_prompt.Get_prompt_variables import Get_prompt_variables
# from myapp.views.Get_prompt.Get_current_date_and_time import get_current_date_by_location, get_current_time_by_location
# from myapp.views.Get_prompt.Get_hours_of_operation import get_hours_of_operation_info
# from myapp.views.Get_prompt.Get_jump_pass import get_jump_pass_flow_prompt, get_jump_pass_info
# from myapp.views.Get_prompt.Get_membership import get_membership_flow_prompt, get_membership_info
# from myapp.views.Get_prompt.Get_FAQs import extract_faqs_for_llm
# from myapp.views.Get_prompt.Get_policy import get_policies_for_llm
# from myapp.views.Get_prompt.Get_RentalFacility import get_rental_facility_info
# from myapp.views.Get_prompt.Get_Birthday_party_packages import load_birthday_party_flow_prompt
# from myapp.views.Get_prompt.Get_Static_text_functions import starting_guidelines_test, current_time_information
# from myapp.views.Get_prompt.Get_location_and_available_items import create_location_info_prompt

# # Helper function to get location name (you might need to implement this)
# async def get_location_name(location_id):
#     """
#     Get location name from database
#     You need to implement this based on your models
#     """
#     try:
#         # Example implementation - adjust based on your models
#         from myapp.models import Location
#         location = await Location.objects.aget(id=location_id)
#         return location.name if location else f"Location_{location_id}"
#     except:
#         return f"Location_{location_id}"

# # API 1: Create Starting Guidelines Prompt
# async def create_starting_guidelines_prompt(request):
#     try:
#         starting_guidelines = await starting_guidelines_test()
        
#         # Create folder with generic name since no location_id
#         folder_name, folder_path = create_location_folder("general", "System_Guidelines")
        
#         # Save to markdown file
#         file_path = save_markdown_file(
#             folder_path, 
#             'starting_guidelines_prompt.md',
#             starting_guidelines
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Starting guidelines prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "starting_guidelines_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 2: Create Current Time Information Prompt
# async def create_current_time_info_prompt(request, timezone="Asia/Karachi"):
#     try:
#         current_time_info = await current_time_information(timezone)
        
#         folder_name, folder_path = create_location_folder("timezone", f"Timezone_{timezone}")
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'current_time_info_prompt.md',
#             current_time_info
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Current time info prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "current_time_info_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 3: Create Current Date Prompt
# async def create_current_date_prompt(request, location_id):
#     try:
#         current_date = await get_current_date_by_location(location_id)
        
#         # Get location name for folder
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'current_date_prompt.md',
#             current_date
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Current date prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "current_date_prompt.md",
#             "current_date": current_date
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 4: Create Current Time Prompt
# async def create_current_time_prompt(request, location_id):
#     try:
#         current_time = await get_current_time_by_location(location_id)
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'current_time_prompt.md',
#             current_time
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Current time prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "current_time_prompt.md",
#             "current_time": current_time
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 5: Create Birthday Party Package Prompt
# async def create_birthday_party_prompt(request, location_id, search_number, client_id):
#     try:
#         timezone = "Asia/Karachi"
        
#         # Get birthday party package info
#         birthday_party_info = await load_birthday_party_flow_prompt(location_id, timezone, search_number, client_id)
        
#         # Get location name for folder
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         # Save system message
#         file_path = save_markdown_file(
#             folder_path, 
#             'birthday_party_package_prompt.md',
#             birthday_party_info.get('system_message', '')
#         )
        
#         # Also save customer information if available
#         if birthday_party_info.get('customer_information'):
#             customer_file = save_markdown_file(
#                 folder_path,
#                 'birthday_customer_info.md',
#                 str(birthday_party_info.get('customer_information', {}))
#             )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Birthday party package prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "birthday_party_package_prompt.md",
#             "has_customer_info": 'customer_information' in birthday_party_info
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 6: Create Jump Pass Flow Prompt
# async def create_jump_pass_flow_prompt_api(request, location_id):
#     try:
#         timezone = "Asia/Karachi"
        
#         # Get jump pass flow prompt
#         jump_pass_prompt = await get_jump_pass_flow_prompt(location_id, timezone)
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'jump_pass_prompt.md',
#             jump_pass_prompt
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Jump pass flow prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "jump_pass_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 7: Create Jump Pass Info Prompt
# async def create_jump_pass_info_prompt(request, location_id):
#     try:
#         timezone = "Asia/Karachi"
        
#         # Get jump pass info
#         jump_pass_info = await get_jump_pass_info(location_id, timezone)
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'jump_pass_info_prompt.md',
#             str(jump_pass_info)
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Jump pass info prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "jump_pass_info_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 8: Create Membership Flow Prompt
# async def create_membership_flow_prompt_api(request, location_id):
#     try:
#         timezone = "Asia/Karachi"
        
#         # Get membership flow prompt
#         membership_prompt = await get_membership_flow_prompt(location_id, timezone)
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'membership_prompt.md',
#             membership_prompt
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Membership flow prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "membership_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 9: Create Membership Info Prompt
# async def create_membership_info_prompt(request, location_id):
#     try:
#         timezone = "Asia/Karachi"
        
#         # Get membership info
#         membership_info = await get_membership_info(location_id, timezone)
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'membership_info_prompt.md',
#             str(membership_info)
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Membership info prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "membership_info_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 10: Create Hours of Operation Prompt
# async def create_hours_of_operation_prompt(request, location_id):
#     try:
#         timezone = "Asia/Karachi"
        
#         # Get hours of operation info
#         hours_info = await get_hours_of_operation_info(location_id, timezone)
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'hours_of_operation_prompt.md',
#             hours_info
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Hours of operation prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "hours_of_operation_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 11: Create FAQs Prompt
# async def create_faqs_prompt(request, location_id):
#     try:
#         # Get FAQs info
#         faqs_info = await extract_faqs_for_llm(location_id)
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'faqs_prompt.md',
#             faqs_info
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "FAQs prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "faqs_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 12: Create Policies Prompt
# async def create_policies_prompt(request, location_id):
#     try:
#         # Get policies info
#         policies_info = await get_policies_for_llm(location_id)
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'policies_prompt.md',
#             policies_info.get('formatted_policies', '')
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Policies prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "policies_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 13: Create Rental Facility Prompt
# async def create_rental_facility_prompt(request, location_id):
#     try:
#         # Get rental facility info
#         rental_info = await get_rental_facility_info(location_id, "yes")
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'rental_facility_prompt.md',
#             rental_info.get('formatted_prompt', '')
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Rental facility prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "rental_facility_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 14: Create Location Info Prompt
# async def create_location_info_prompt_api(request, location_id):
#     try:
#         # Get location info
#         location_info = await create_location_info_prompt(location_id)
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'location_info_prompt.md',
#             location_info.get('location_prompt', '')
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Location info prompt created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "location_info_prompt.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 15: Create Prompt Variables
# async def create_prompt_variables_prompt(request, location_id):
#     try:
#         # Get prompt variables
#         prompt_variables = await Get_prompt_variables(location_id)
        
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         file_path = save_markdown_file(
#             folder_path, 
#             'prompt_variables.md',
#             str(prompt_variables)
#         )
        
#         return JsonResponse({
#             "status": "success",
#             "message": "Prompt variables created successfully",
#             "folder_name": folder_name,
#             "file_path": file_path,
#             "file_name": "prompt_variables.md"
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 16: Get Combined Prompt (returns all prompts combined without saving)
# async def get_combined_all_prompts(request, location_id, search_number, client_id):
#     try:
#         timezone = "Asia/Karachi"
        
#         # Get ALL the data
#         starting_guidelines = await starting_guidelines_test()
#         current_time_info = await current_time_information(timezone)
#         current_date = await get_current_date_by_location(location_id)
#         current_time = await get_current_time_by_location(location_id)
#         birthday_party_info = await load_birthday_party_flow_prompt(location_id, timezone, search_number, client_id)
#         jump_pass_flow = await get_jump_pass_flow_prompt(location_id, timezone)
#         jump_pass_info_data = await get_jump_pass_info(location_id, timezone)
#         membership_flow = await get_membership_flow_prompt(location_id, timezone)
#         membership_info_data = await get_membership_info(location_id, timezone)
#         hours_info = await get_hours_of_operation_info(location_id, timezone)
#         faqs_info = await extract_faqs_for_llm(location_id)
#         policies_info = await get_policies_for_llm(location_id)
#         rental_info = await get_rental_facility_info(location_id, "yes")
#         location_info = await create_location_info_prompt(location_id)
#         prompt_variables = await Get_prompt_variables(location_id)
        
#         # Combine all prompts in the exact same format as your original
#         combined_prompt = f"""
# {starting_guidelines}
# ## Call Context
# {current_time_info}
# ## Birthday Party Packages
# {birthday_party_info.get('system_message', '')}
# ## Start Of Memberships Flow
# {membership_flow}
# ## End Of Memberships Flow
# ## Start Of Jump Passes Flow
# {jump_pass_flow}
# ## End Of Jump Passes Flow
# ## Hours of Operation
# {hours_info}
# ## Location
# {location_info.get('location_prompt', '')}
# ## FAQs
# {faqs_info}
# ## Policies
# {policies_info.get('formatted_policies', '')}
# ## Rental Facilities
# {rental_info.get('formatted_prompt', '')}
# """
        
#         # Get location name
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         return JsonResponse({
#             "status": "success",
#             "combined_prompt": combined_prompt,
#             "folder_name": folder_name,
#             "message": "All prompts combined successfully",
#             "sections_included": [
#                 "starting_guidelines",
#                 "current_time_info",
#                 "birthday_party_packages",
#                 "membership_flow",
#                 "jump_pass_flow",
#                 "hours_of_operation",
#                 "location_info",
#                 "faqs",
#                 "policies",
#                 "rental_facilities"
#             ],
#             "metadata": {
#                 "location_id": location_id,
#                 "location_name": location_name,
#                 "current_date": current_date,
#                 "current_time": current_time,
#                 "customer_information": birthday_party_info.get('customer_information', {})
#             }
#         }, status=200)
        
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=500)

# # API 17: Create ALL Prompts at Once (creates individual files + combined file)
# async def create_all_prompts_at_once(request, location_id, search_number, client_id):
#     try:
#         timezone = "Asia/Karachi"
        
#         # Get location name
#         location_name = await get_location_name(location_id)
#         folder_name, folder_path = create_location_folder(location_id, location_name)
        
#         files_created = []
        
#         # 1. Starting Guidelines
#         try:
#             starting_guidelines = await starting_guidelines_test()
#             file_path = save_markdown_file(
#                 folder_path, 'starting_guidelines_prompt.md', starting_guidelines
#             )
#             files_created.append("starting_guidelines_prompt.md")
#         except Exception as e:
#             print(f"Error creating starting guidelines: {e}")
        
#         # 2. Current Time Information
#         try:
#             current_time_info = await current_time_information(timezone)
#             file_path = save_markdown_file(
#                 folder_path, 'current_time_info_prompt.md', current_time_info
#             )
#             files_created.append("current_time_info_prompt.md")
#         except Exception as e:
#             print(f"Error creating current time info: {e}")
        
#         # 3. Current Date
#         try:
#             current_date = await get_current_date_by_location(location_id)
#             file_path = save_markdown_file(
#                 folder_path, 'current_date_prompt.md', current_date
#             )
#             files_created.append("current_date_prompt.md")
#         except Exception as e:
#             print(f"Error creating current date: {e}")
        
#         # 4. Current Time
#         try:
#             current_time = await get_current_time_by_location(location_id)
#             file_path = save_markdown_file(
#                 folder_path, 'current_time_prompt.md', current_time
#             )
#             files_created.append("current_time_prompt.md")
#         except Exception as e:
#             print(f"Error creating current time: {e}")
        
#         # 5. Birthday Party Package
#         try:
#             birthday_party_info = await load_birthday_party_flow_prompt(location_id, timezone, search_number, client_id)
#             file_path = save_markdown_file(
#                 folder_path, 'birthday_party_package_prompt.md', 
#                 birthday_party_info.get('system_message', '')
#             )
#             files_created.append("birthday_party_package_prompt.md")
#         except Exception as e:
#             print(f"Error creating birthday party: {e}")
        
#         # 6. Jump Pass Flow
#         try:
#             jump_pass_flow = await get_jump_pass_flow_prompt(location_id, timezone)
#             file_path = save_markdown_file(
#                 folder_path, 'jump_pass_prompt.md', jump_pass_flow
#             )
#             files_created.append("jump_pass_prompt.md")
#         except Exception as e:
#             print(f"Error creating jump pass flow: {e}")
        
#         # 7. Jump Pass Info
#         try:
#             jump_pass_info_data = await get_jump_pass_info(location_id, timezone)
#             file_path = save_markdown_file(
#                 folder_path, 'jump_pass_info_prompt.md', str(jump_pass_info_data)
#             )
#             files_created.append("jump_pass_info_prompt.md")
#         except Exception as e:
#             print(f"Error creating jump pass info: {e}")
        
#         # 8. Membership Flow
#         try:
#             membership_flow = await get_membership_flow_prompt(location_id, timezone)
#             file_path = save_markdown_file(
#                 folder_path, 'membership_prompt.md', membership_flow
#             )
#             files_created.append("membership_prompt.md")
#         except Exception as e:
#             print(f"Error creating membership flow: {e}")
        
#         # 9. Membership Info
#         try:
#             membership_info_data = await get_membership_info(location_id, timezone)
#             file_path = save_markdown_file(
#                 folder_path, 'membership_info_prompt.md', str(membership_info_data)
#             )
#             files_created.append("membership_info_prompt.md")
#         except Exception as e:
#             print(f"Error creating membership info: {e}")
        
#         # 10. Hours of Operation
#         try:
#             hours_info = await get_hours_of_operation_info(location_id, timezone)
#             file_path = save_markdown_file(
#                 folder_path, 'hours_of_operation_prompt.md', hours_info
#             )
#             files_created.append("hours_of_operation_prompt.md")
#         except Exception as e:
#             print(f"Error creating hours of operation: {e}")
        
#         # 11. FAQs
#         try:
#             faqs_info = await extract_faqs_for_llm(location_id)
#             file_path = save_markdown_file(
#                 folder_path, 'faqs_prompt.md', faqs_info
#             )
#             files_created.append("faqs_prompt.md")
#         except Exception as e:
#             print(f"Error creating FAQs: {e}")
        
#         # 12. Policies
#         try:
#             policies_info = await get_policies_for_llm(location_id)
#             file_path = save_markdown_file(
#                 folder_path, 'policies_prompt.md', policies_info.get('formatted_policies', '')
#             )
#             files_created.append("policies_prompt.md")
#         except Exception as e:
#             print(f"Error creating policies: {e}")
        
#         # 13. Rental Facility
#         try:
#             rental_info = await get_rental_facility_info(location_id, "yes")
#             file_path = save_markdown_file(
#                 folder_path, 'rental_facility_prompt.md', rental_info.get('formatted_prompt', '')
#             )
#             files_created.append("rental_facility_prompt.md")
#         except Exception as e:
#             print(f"Error creating rental facility: {e}")
        
#         # 14. Location Info
#         try:
#             location_info = await create_location_info_prompt(location_id)
#             file_path = save_markdown_file(
#                 folder_path, 'location_info_prompt.md', location_info.get('location_prompt', '')
#             )
#             files_created.append("location_info_prompt.md")
#         except Exception as e:
#             print(f"Error creating location info: {e}")
        
#         # 15. Prompt Variables
#         try:
#             prompt_variables = await Get_prompt_variables(location_id)
#             file_path = save_markdown_file(
#                 folder_path, 'prompt_variables.md', str(prompt_variables)
#             )
#             files_created.append("prompt_variables.md")
#         except Exception as e:
#             print(f"Error creating prompt variables: {e}")
        
#         # 16. Create combined file
#         try:
#             # combined_content, combined_file_path, files_included = combine_all_prompts(folder_path)
            
#             files_created.append("combined_all_prompts.md")
#         except Exception as e:
#             print(f"Error creating combined file: {e}")
#             combined_content = ""
#             files_included = []
        
#         return JsonResponse({
#             "status": "success",
#             "message": f"All prompts created successfully in folder: {folder_name}",
#             "folder_name": folder_name,
#             "folder_path": folder_path,
#             "total_files_created": len(files_created),
#             "files_created": files_created,
#             "files_in_combined": files_included
#         }, status=200)
        
#     except Exception as e:
#         returonResponse({"error": str(e)}, status=500)














# myapp/views/Individual_Prompts/create_individual_prompts.py
import os
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
from myapp.utils.prompt_file_utils import (
    get_location_folder_path, 
    save_markdown_file, 
    combine_all_prompts_for_location,
    get_location_files_info
)
from myapp.views.Get_prompt.Get_prompt_variables import Get_prompt_variables
from myapp.views.Get_prompt.Get_current_date_and_time import get_current_date_by_location, get_current_time_by_location
from myapp.views.Get_prompt.Get_hours_of_operation import get_hours_of_operation_info
from myapp.views.Get_prompt.Get_jump_pass import get_jump_pass_flow_prompt, get_jump_pass_info
from myapp.views.Get_prompt.Get_membership import get_membership_flow_prompt, get_membership_info
from myapp.views.Get_prompt.Get_FAQs import extract_faqs_for_llm
from myapp.views.Get_prompt.Get_policy import get_policies_for_llm
from myapp.views.Get_prompt.Get_RentalFacility import get_rental_facility_info
from myapp.views.Get_prompt.Get_Birthday_party_packages import load_birthday_party_flow_prompt
from myapp.views.Get_prompt.Get_Static_text_functions import starting_guidelines_test, current_time_information
from myapp.views.Get_prompt.Get_location_and_available_items import create_location_info_prompt

# Helper function to get location name
async def get_location_name(location_id):
    """
    Get location name from database
    You need to implement this based on your models
    """
    try:
        # Example implementation - adjust based on your models
        from myapp.models import Location
        location = await Location.objects.aget(id=location_id)
        return location.name if location else f"Location_{location_id}"
    except Exception as e:
        print(f"Error getting location name: {e}")
        return f"Location_{location_id}"

# API 1: Create Starting Guidelines Prompt
async def create_starting_guidelines_prompt(request):
    try:
        starting_guidelines = await starting_guidelines_test()
        
        # Create general folder for system prompts
        folder_name, folder_path = get_location_folder_path("system", "System_Prompts")
        
        # Save to markdown file
        file_path = save_markdown_file(
            folder_path, 
            'starting_guidelines_prompt.md',
            starting_guidelines
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Starting guidelines prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "starting_guidelines_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 2: Create Current Time Information Prompt
async def create_current_time_info_prompt(request, timezone="Asia/Karachi"):
    try:
        current_time_info = await current_time_information(timezone)
        
        folder_name, folder_path = get_location_folder_path("system", "System_Prompts")
        
        file_path = save_markdown_file(
            folder_path, 
            'current_time_info_prompt.md',
            current_time_info
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Current time info prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "current_time_info_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 3: Create Current Date Prompt
async def create_current_date_prompt(request, location_id):
    try:
        current_date = await get_current_date_by_location(location_id)
        
        # Get location name for folder
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'current_date_prompt.md',
            current_date
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Current date prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "current_date_prompt.md",
            "current_date": current_date
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 4: Create Current Time Prompt
async def create_current_time_prompt(request, location_id):
    try:
        current_time = await get_current_time_by_location(location_id)
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'current_time_prompt.md',
            current_time
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Current time prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "current_time_prompt.md",
            "current_time": current_time
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 5: Create Birthday Party Package Prompt
async def create_birthday_party_prompt(request, location_id, search_number, client_id):
    try:
        timezone = "Asia/Karachi"
        
        # Get birthday party package info
        birthday_party_info = await load_birthday_party_flow_prompt(location_id, timezone, search_number, client_id)
        
        # Get location name for folder
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        # Save system message
        file_path = save_markdown_file(
            folder_path, 
            'birthday_party_package_prompt.md',
            birthday_party_info.get('system_message', '')
        )
        
        # Also save customer information if available
        if birthday_party_info.get('customer_information'):
            customer_file = save_markdown_file(
                folder_path,
                'birthday_customer_info.md',
                str(birthday_party_info.get('customer_information', {}))
            )
        
        return JsonResponse({
            "status": "success",
            "message": "Birthday party package prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "birthday_party_package_prompt.md",
            "has_customer_info": 'customer_information' in birthday_party_info
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 6: Create Jump Pass Flow Prompt
async def create_jump_pass_flow_prompt_api(request, location_id):
    try:
        timezone = "Asia/Karachi"
        
        # Get jump pass flow prompt
        jump_pass_prompt = await get_jump_pass_flow_prompt(location_id, timezone)
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'jump_pass_prompt.md',
            jump_pass_prompt
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Jump pass flow prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "jump_pass_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 7: Create Jump Pass Info Prompt
async def create_jump_pass_info_prompt(request, location_id):
    try:
        timezone = "Asia/Karachi"
        
        # Get jump pass info
        jump_pass_info = await get_jump_pass_info(location_id, timezone)
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'jump_pass_info_prompt.md',
            str(jump_pass_info)
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Jump pass info prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "jump_pass_info_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 8: Create Membership Flow Prompt
async def create_membership_flow_prompt_api(request, location_id):
    try:
        timezone = "Asia/Karachi"
        
        # Get membership flow prompt
        membership_prompt = await get_membership_flow_prompt(location_id, timezone)
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'membership_prompt.md',
            membership_prompt
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Membership flow prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "membership_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 9: Create Membership Info Prompt
async def create_membership_info_prompt(request, location_id):
    try:
        timezone = "Asia/Karachi"
        
        # Get membership info
        membership_info = await get_membership_info(location_id, timezone)
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'membership_info_prompt.md',
            str(membership_info)
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Membership info prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "membership_info_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 10: Create Hours of Operation Prompt
async def create_hours_of_operation_prompt(request, location_id):
    try:
        timezone = "Asia/Karachi"
        
        # Get hours of operation info
        hours_info = await get_hours_of_operation_info(location_id, timezone)
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'hours_of_operation_prompt.md',
            hours_info
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Hours of operation prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "hours_of_operation_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 11: Create FAQs Prompt
async def create_faqs_prompt(request, location_id):
    try:
        # Get FAQs info
        faqs_info = await extract_faqs_for_llm(location_id)
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'faqs_prompt.md',
            faqs_info
        )
        
        return JsonResponse({
            "status": "success",
            "message": "FAQs prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "faqs_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 12: Create Policies Prompt
async def create_policies_prompt(request, location_id):
    try:
        # Get policies info
        policies_info = await get_policies_for_llm(location_id)
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'policies_prompt.md',
            policies_info.get('formatted_policies', '')
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Policies prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "policies_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 13: Create Rental Facility Prompt
async def create_rental_facility_prompt(request, location_id):
    try:
        # Get rental facility info
        rental_info = await get_rental_facility_info(location_id, "yes")
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'rental_facility_prompt.md',
            rental_info.get('formatted_prompt', '')
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Rental facility prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "rental_facility_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 14: Create Location Info Prompt
async def create_location_info_prompt_api(request, location_id):
    try:
        # Get location info
        location_info = await create_location_info_prompt(location_id)
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'location_info_prompt.md',
            location_info.get('location_prompt', '')
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Location info prompt created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "location_info_prompt.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 15: Create Prompt Variables
async def create_prompt_variables_prompt(request, location_id):
    try:
        # Get prompt variables
        prompt_variables = await Get_prompt_variables(location_id)
        
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        file_path = save_markdown_file(
            folder_path, 
            'prompt_variables.md',
            str(prompt_variables)
        )
        
        return JsonResponse({
            "status": "success",
            "message": "Prompt variables created/updated successfully",
            "folder_name": folder_name,
            "file_path": file_path,
            "file_name": "prompt_variables.md"
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 16: Get Combined Prompt - Reads from existing files and combines them
async def get_combined_all_prompts(request, location_id):
    try:
        # Get location name
        location_name = await get_location_name(location_id)
        
        # Combine all prompts from the location folder
        combined_content, combined_file_path, files_found = combine_all_prompts_for_location(
            location_id, location_name
        )
        
        return JsonResponse({
            "status": "success",
            "message": "All prompts combined successfully from existing files",
            "folder_name": f"{location_id}_{location_name.replace(' ', '_')}",
            "combined_prompt": combined_content,
            "files_included": files_found,
            "total_files_found": len(files_found),
            "combined_file_path": combined_file_path
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 17: Get location folder info
async def get_location_folder_info(request, location_id):
    try:
        location_name = await get_location_name(location_id)
        folder_info = get_location_files_info(location_id, location_name)
        
        return JsonResponse({
            "status": "success",
            "location_id": location_id,
            "location_name": location_name,
            "folder_info": folder_info
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# API 18: Create ALL Prompts at Once (creates individual files + combined file)
async def create_all_prompts_at_once(request, location_id, search_number, client_id):
    try:
        timezone = "Asia/Karachi"
        
        # Get location name
        location_name = await get_location_name(location_id)
        folder_name, folder_path = get_location_folder_path(location_id, location_name)
        
        files_created = []
        
        # 1. Starting Guidelines
        try:
            starting_guidelines = await starting_guidelines_test()
            file_path = save_markdown_file(
                folder_path, 'starting_guidelines_prompt.md', starting_guidelines
            )
            files_created.append("starting_guidelines_prompt.md")
        except Exception as e:
            print(f"Error creating starting guidelines: {e}")
        
        # 2. Current Time Information
        try:
            current_time_info = await current_time_information(timezone)
            file_path = save_markdown_file(
                folder_path, 'current_time_info_prompt.md', current_time_info
            )
            files_created.append("current_time_info_prompt.md")
        except Exception as e:
            print(f"Error creating current time info: {e}")
        
        # 3. Current Date
        try:
            current_date = await get_current_date_by_location(location_id)
            file_path = save_markdown_file(
                folder_path, 'current_date_prompt.md', current_date
            )
            files_created.append("current_date_prompt.md")
        except Exception as e:
            print(f"Error creating current date: {e}")
        
        # 4. Current Time
        try:
            current_time = await get_current_time_by_location(location_id)
            file_path = save_markdown_file(
                folder_path, 'current_time_prompt.md', current_time
            )
            files_created.append("current_time_prompt.md")
        except Exception as e:
            print(f"Error creating current time: {e}")
        
        # 5. Birthday Party Package
        try:
            birthday_party_info = await load_birthday_party_flow_prompt(location_id, timezone, search_number, client_id)
            file_path = save_markdown_file(
                folder_path, 'birthday_party_package_prompt.md', 
                birthday_party_info.get('system_message', '')
            )
            files_created.append("birthday_party_package_prompt.md")
            
            # Save customer info if available
            if birthday_party_info.get('customer_information'):
                save_markdown_file(
                    folder_path, 'birthday_customer_info.md',
                    str(birthday_party_info.get('customer_information', {}))
                )
                files_created.append("birthday_customer_info.md")
        except Exception as e:
            print(f"Error creating birthday party: {e}")
        
        # 6. Jump Pass Flow
        try:
            jump_pass_flow = await get_jump_pass_flow_prompt(location_id, timezone)
            file_path = save_markdown_file(
                folder_path, 'jump_pass_prompt.md', jump_pass_flow
            )
            files_created.append("jump_pass_prompt.md")
        except Exception as e:
            print(f"Error creating jump pass flow: {e}")
        
        # 7. Jump Pass Info
        try:
            jump_pass_info_data = await get_jump_pass_info(location_id, timezone)
            file_path = save_markdown_file(
                folder_path, 'jump_pass_info_prompt.md', str(jump_pass_info_data)
            )
            files_created.append("jump_pass_info_prompt.md")
        except Exception as e:
            print(f"Error creating jump pass info: {e}")
        
        # 8. Membership Flow
        try:
            membership_flow = await get_membership_flow_prompt(location_id, timezone)
            file_path = save_markdown_file(
                folder_path, 'membership_prompt.md', membership_flow
            )
            files_created.append("membership_prompt.md")
        except Exception as e:
            print(f"Error creating membership flow: {e}")
        
        # 9. Membership Info
        try:
            membership_info_data = await get_membership_info(location_id, timezone)
            file_path = save_markdown_file(
                folder_path, 'membership_info_prompt.md', str(membership_info_data)
            )
            files_created.append("membership_info_prompt.md")
        except Exception as e:
            print(f"Error creating membership info: {e}")
        
        # 10. Hours of Operation
        try:
            hours_info = await get_hours_of_operation_info(location_id, timezone)
            file_path = save_markdown_file(
                folder_path, 'hours_of_operation_prompt.md', hours_info
            )
            files_created.append("hours_of_operation_prompt.md")
        except Exception as e:
            print(f"Error creating hours of operation: {e}")
        
        # 11. FAQs
        try:
            faqs_info = await extract_faqs_for_llm(location_id)
            file_path = save_markdown_file(
                folder_path, 'faqs_prompt.md', faqs_info
            )
            files_created.append("faqs_prompt.md")
        except Exception as e:
            print(f"Error creating FAQs: {e}")
        
        # 12. Policies
        try:
            policies_info = await get_policies_for_llm(location_id)
            file_path = save_markdown_file(
                folder_path, 'policies_prompt.md', policies_info.get('formatted_policies', '')
            )
            files_created.append("policies_prompt.md")
        except Exception as e:
            print(f"Error creating policies: {e}")
        
        # 13. Rental Facility
        try:
            rental_info = await get_rental_facility_info(location_id, "yes")
            file_path = save_markdown_file(
                folder_path, 'rental_facility_prompt.md', rental_info.get('formatted_prompt', '')
            )
            files_created.append("rental_facility_prompt.md")
        except Exception as e:
            print(f"Error creating rental facility: {e}")
        
        # 14. Location Info
        try:
            location_info = await create_location_info_prompt(location_id)
            file_path = save_markdown_file(
                folder_path, 'location_info_prompt.md', location_info.get('location_prompt', '')
            )
            files_created.append("location_info_prompt.md")
        except Exception as e:
            print(f"Error creating location info: {e}")
        
        # 15. Prompt Variables
        try:
            prompt_variables = await Get_prompt_variables(location_id)
            file_path = save_markdown_file(
                folder_path, 'prompt_variables.md', str(prompt_variables)
            )
            files_created.append("prompt_variables.md")
        except Exception as e:
            print(f"Error creating prompt variables: {e}")
        
        # 16. Create combined file
        try:
            combined_content, combined_file_path, files_included = combine_all_prompts_for_location(
                location_id, location_name
            )
            files_created.append("combined_all_prompts.md")
        except Exception as e:
            print(f"Error creating combined file: {e}")
            combined_content = ""
            files_included = []
        
        return JsonResponse({
            "status": "success",
            "message": f"All prompts created/updated successfully in location folder: {folder_name}",
            "folder_name": folder_name,
            "folder_path": folder_path,
            "total_files_created": len(files_created),
            "files_created": files_created,
            "files_in_combined": files_included,
            "combined_content_length": len(combined_content) if combined_content else 0
        }, status=200)
        
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)