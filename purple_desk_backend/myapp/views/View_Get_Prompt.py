# In View_Get_Prompt.py
from myapp.views.Get_prompt.Get_hours_of_operation import get_hours_of_operation_info
from myapp.views.Get_prompt.Get_jump_pass import get_jump_pass_info
from django.http import JsonResponse
from asgiref.sync import sync_to_async

async def get_prompt(request, location_id):
    try:
        # ... your existing code ...
        
        # Get timezone (you'll need to get this from your location model)
        # Assuming you have a way to get the timezone for the location
        # timezone = "America/Los_Angeles"  # Replace with actual timezone from your location
        timezone = "Asia/Karachi"

        
        # Get hours of operation from database
        hours_of_operation_info = await get_hours_of_operation_info(location_id, timezone)
        jump_pass_info = await get_jump_pass_info(location_id, timezone)
        print("Hours of Operation Info:", hours_of_operation_info)
        print("jump_pass_info Info:", jump_pass_info['jump_passes_info'])

        

        
        return JsonResponse({"prompt":jump_pass_info['jump_passes_info']} ,status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
        