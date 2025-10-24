# import json
# from django.http import JsonResponse
# from rest_framework import status
# from rest_framework.decorators import permission_classes
# from rest_framework.permissions import IsAdminUser
# from asgiref.sync import sync_to_async
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from myapp.model.hours_of_operations_model import HoursOfOperation
# from myapp.serializers import HoursOfOperationSerializer
# from django.http import HttpResponse



# async def require_admin(request):
#     try:
#         user_auth_tuple = await sync_to_async(JWTAuthentication().authenticate)(request)
#     except AuthenticationFailed as e:
#         return None, JsonResponse({"detail": str(e)}, status=401)

#     if not user_auth_tuple:
#         return None, JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

#     user, token = user_auth_tuple
#     if not user.is_authenticated or not user.is_staff:
#         return None, JsonResponse({"detail": "You do not have permission to perform this action."}, status=403)

#     return user, None



# async def create_hours_of_operation(request, location_id):
#     try:
#         user, error_response = await require_admin(request)
#         if error_response:
#             return error_response
#         body = await sync_to_async(request.body.decode)('utf-8')
#         data = json.loads(body)
#         data["location"] = location_id   # attach FK
        
#         restricted_types = ["early_closing", "late_closing", "early_opening", "late_opening"]
#         if data.get("hours_type") in restricted_types:
#             if not data.get("reason") or not data.get("starting_date"):
#                 return JsonResponse(
#                     {"error": "For early_closing, late_closing, early_opening, late_opening 'reason' and 'starting_date' are required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             data.setdefault("schedule_with", "N/A")
#             data.setdefault("ages_allowed", "N/A")
#         if data.get("hours_type") == "special":
#             if not data.get("schedule_with") or not data.get("starting_date") or not data.get("ages_allowed"):
#                 return JsonResponse(
#                     {"error": "For special, 'ages allowed' and 'starting_date' is required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#         if data.get("hours_type") == "closed":
#             if not data.get("starting_date") or not data.get("reason"):
#                 return JsonResponse(
#                     {"error": "For closed, 'starting' and 'reason' is required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             data.setdefault("schedule_with", "closed")
#             data.setdefault("ages_allowed", "closed")
#             data.setdefault("start_time", "00:00:00")
#             data.setdefault("end_time", "00:00:00")
        
#         serializer = HoursOfOperationSerializer(data=data)
#         is_valid = await sync_to_async(serializer.is_valid)()
#         if is_valid:
#             await sync_to_async(serializer.save)()
#             return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
#         print("This is the error:", serializer.errors)
#         return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     except Exception as e:
#         print("This is the error:", str(e))
#         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# async def get_hours_of_operations(request, location_id):
#     try:
#         # Fixed: Use JsonResponse instead of manual HttpResponse + json.dumps
#         user, error_response = await require_admin(request)
#         if error_response:
#             return error_response
#         hours = await sync_to_async(lambda: list(HoursOfOperation.objects.filter(location_id=location_id)))()
#         serializer = HoursOfOperationSerializer(hours, many=True)
#         return JsonResponse(serializer.data, safe=False, status=200)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# # @permission_classes([IsAdminUser])
# # async def get_hours_of_operation(request, location_id, pk):
# #     try:
# #         hours = await sync_to_async(HoursOfOperation.objects.get)(pk=pk, location_id=location_id)
# #         serializer = HoursOfOperationSerializer(hours)
# #         return JsonResponse(serializer.data, status=status.HTTP_200_OK)
# #     except HoursOfOperation.DoesNotExist:
# #         return JsonResponse({"error": "Hours of Operation not found"}, status=status.HTTP_404_NOT_FOUND)
# #     except Exception as e:
# #         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# async def update_hours_of_operation(request, location_id, pk):
#     try:
#         user, error_response = await require_admin(request)
#         if error_response:
#             return error_response
#         hours = await sync_to_async(HoursOfOperation.objects.get)(pk=pk, location_id=location_id)
        
#         # Fixed: Make body decoding async
#         body = await sync_to_async(request.body.decode)('utf-8')
#         data = json.loads(body)
#         data["location"] = location_id   # keep FK intact
        
#         # custom validation
#         restricted_types = ["special", "early_closing", "late_closing", "early_opening", "late_opening"]
#         if data.get("hours_type") in restricted_types:
#             if not data.get("reason") or not data.get("starting_date"):
#                 return JsonResponse(
#                     {"error": "For special/closing/opening hours, 'reason' and 'starting_date' are required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
        
#         serializer = HoursOfOperationSerializer(hours, data=data)
#         is_valid = await sync_to_async(serializer.is_valid)()
#         if is_valid:
#             await sync_to_async(serializer.save)()
#             return JsonResponse(serializer.data, status=status.HTTP_200_OK)
#         print("This is the error:", serializer.errors)
#         return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     except HoursOfOperation.DoesNotExist:
#         return JsonResponse({"error": "Hours of Operation not found"}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# async def delete_hours_of_operation(request, location_id, pk):
#     try:
#         user, error_response = await require_admin(request)
#         if error_response:
#             return error_response
#         hours = await sync_to_async(HoursOfOperation.objects.get)(pk=pk, location_id=location_id)
#         await sync_to_async(hours.delete)()
        
#         # Fixed: Use JsonResponse instead of manual HttpResponse
#         # Note: 204 No Content should not have a response body, but if you need a message, use 200
#         return JsonResponse({"message": "Hours of Operation deleted successfully"}, status=200)
        
#         # OR for proper 204 No Content (no body):
#         # return HttpResponse(status=204)
#     except HoursOfOperation.DoesNotExist:
#         return JsonResponse({"error": "Hours of Operation not found"}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    





# # views.py - Updated with same_entry_id support
# import json
# import uuid
# from datetime import datetime, timedelta
# from django.http import JsonResponse
# from rest_framework import status
# from rest_framework.decorators import permission_classes
# from rest_framework.permissions import IsAdminUser
# from asgiref.sync import sync_to_async
# from rest_framework_simplejwt.authentication import JWTAuthentication
# from rest_framework.exceptions import AuthenticationFailed
# from myapp.model.hours_of_operations_model import HoursOfOperation
# from myapp.serializers import HoursOfOperationSerializer

# async def require_admin(request):
#     try:
#         user_auth_tuple = await sync_to_async(JWTAuthentication().authenticate)(request)
#     except AuthenticationFailed as e:
#         return None, JsonResponse({"detail": str(e)}, status=401)

#     if not user_auth_tuple:
#         return None, JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

#     user, token = user_auth_tuple
#     if not user.is_authenticated or not user.is_staff:
#         return None, JsonResponse({"detail": "You do not have permission to perform this action."}, status=403)

#     return user, None

# # def create_date_range_entries(data, same_entry_id):
# #     """Create multiple entries for date range with same same_entry_id"""
# #     entries = []
# #     start_date = datetime.strptime(data["starting_date"], "%Y-%m-%d").date()
# #     end_date = datetime.strptime(data["ending_date"], "%Y-%m-%d").date()

# #     print("This is the same_endtry id = == =" , same_entry_id)
# #     print("This is the data - - == = =" , data)
    
# #     current_date = start_date
# #     while current_date <= end_date:
# #         entry_data = data.copy()
# #         entry_data["starting_date"] = current_date
# #         entry_data["ending_date"] = current_date
# #         entry_data["starting_day_name"] = current_date.strftime("%A")
# #         entry_data["ending_day_name"] = current_date.strftime("%A")
# #         entry_data["same_entry_id"] = same_entry_id
        
# #         serializer = HoursOfOperationSerializer(data=entry_data)
# #         if serializer.is_valid():
# #             entries.append(serializer.save())
# #         else:
# #             raise Exception(f"Validation error for date {current_date}: {serializer.errors}")
        
# #         current_date += timedelta(days=1)
    
# #     return entries

# # async def create_hours_of_operation(request, location_id):
# #     try:
# #         user, error_response = await require_admin(request)
# #         if error_response:
# #             return error_response
        
# #         body = await sync_to_async(request.body.decode)('utf-8')
# #         print("this is the data = = boitd = =d=d " , body)
# #         data = json.loads(body)
# #         data["location"] = location_id
# #         # same_entry_id = data["same_entry_id"]


# #         # Generate same_entry_id for new entries
# #         same_entry_id = uuid.uuid4()


# #         # For multi-day special hours, create multiple entries
# #         if (data.get("hours_type") == "special" and 
# #             data.get("starting_date") and 
# #             data.get("ending_date") and
# #             data["starting_date"] != data["ending_date"]):
            
# #             entries = await sync_to_async(create_date_range_entries)(data, same_entry_id)
# #             # Return the first entry as response
# #             serializer = HoursOfOperationSerializer(entries[0])
# #             return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        
# #         # For single day entries
# #         data["same_entry_id"] = same_entry_id
        
# #         restricted_types = ["early_closing", "late_closing", "early_opening", "late_opening"]
# #         if data.get("hours_type") in restricted_types:
# #             if not data.get("reason") or not data.get("starting_date"):
# #                 return JsonResponse(
# #                     {"error": "For early_closing, late_closing, early_opening, late_opening 'reason' and 'starting_date' are required."},
# #                     status=status.HTTP_400_BAD_REQUEST
# #                 )
# #             data.setdefault("schedule_with", "N/A")
# #             data.setdefault("ages_allowed", "N/A")
        
# #         if data.get("hours_type") == "special":
# #             if not data.get("schedule_with") or not data.get("starting_date") or not data.get("ages_allowed"):
# #                 return JsonResponse(
# #                     {"error": "For special, 'ages allowed' and 'starting_date' is required"},
# #                     status=status.HTTP_400_BAD_REQUEST
# #                 )
        
# #         if data.get("hours_type") == "closed":
# #             if not data.get("starting_date") or not data.get("reason"):
# #                 return JsonResponse(
# #                     {"error": "For closed, 'starting' and 'reason' is required"},
# #                     status=status.HTTP_400_BAD_REQUEST
# #                 )
# #             data.setdefault("schedule_with", "closed")
# #             data.setdefault("ages_allowed", "closed")
# #             data.setdefault("start_time", "00:00:00")
# #             data.setdefault("end_time", "00:00:00")
        
# #         # serializer = HoursOfOperationSerializer(data=data)
# #         # is_valid = await sync_to_async(serializer.is_valid)()
# #         # if is_valid:
# #             await sync_to_async(serializer.save)()
# #             return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        
# #         serializer = HoursOfOperationSerializer(data=data)
# #         is_valid = await sync_to_async(serializer.is_valid)()
# #         if is_valid:
# #             # Save the instance and manually set same_entry_id
# #             instance = await sync_to_async(serializer.save)()
            
# #             # If same_entry_id wasn't set by serializer, set it manually
# #             if not instance.same_entry_id:
# #                 instance.same_entry_id = same_entry_id
# #                 await sync_to_async(instance.save)()
            
# #             # Refresh serializer data to include the same_entry_id
# #             updated_serializer = HoursOfOperationSerializer(instance)
# #             return JsonResponse(updated_serializer.data, status=status.HTTP_201_CREATED)

# #             print("This is the error:", serializer.errors)
# #         return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
# #     except Exception as e:
# #         print("This is the error:", str(e))
# #         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# def create_date_range_entries(data, same_entry_id):
#     """
#     Synchronous helper to create multiple HoursOfOperation rows for each date
#     in a range. This uses serializer.save(same_entry_id=same_entry_id) so the
#     read-only same_entry_id is still written by the server.
#     Raises Exception on validation error.
#     Returns list of created model instances.
#     """
#     from datetime import datetime, timedelta

#     entries = []
#     start_date = datetime.strptime(data["starting_date"], "%Y-%m-%d").date()
#     end_date = datetime.strptime(data["ending_date"], "%Y-%m-%d").date()

#     current_date = start_date
#     while current_date <= end_date:
#         entry_data = data.copy()
#         # ensure date fields are date objects/strings expected by serializer
#         entry_data["starting_date"] = current_date.isoformat()
#         entry_data["ending_date"] = current_date.isoformat()
#         entry_data["starting_day_name"] = current_date.strftime("%A")
#         entry_data["ending_day_name"] = current_date.strftime("%A")
#         # Do NOT set same_entry_id in entry_data if it's read-only; we'll pass it to save()
#         serializer = HoursOfOperationSerializer(data=entry_data)
#         if serializer.is_valid():
#             # pass server-generated same_entry_id into save()
#             instance = serializer.save(same_entry_id=same_entry_id)
#             entries.append(instance)
#         else:
#             # Raise so the async caller can return 400 or handle it
#             raise Exception(f"Validation error for date {current_date}: {serializer.errors}")
#         current_date += timedelta(days=1)

#     return entries


# async def create_hours_of_operation(request, location_id):
#     """
#     Async view for creating HoursOfOperation entries.
#     - Generates a server-side same_entry_id (UUID) and passes it into serializer.save(...)
#       so it will be stored even if the field is read-only in the serializer.
#     - Supports multi-day 'special' entries (creates one DB row per date in range).
#     """
#     try:
#         # auth
#         user, error_response = await require_admin(request)
#         if error_response:
#             return error_response

#         # parse body
#         body = await sync_to_async(request.body.decode)('utf-8')
#         data = json.loads(body)
#         data["location"] = location_id

#         # generate server-side same_entry_id
#         same_entry_id = uuid.uuid4()

#         # Validate required fields for restricted types early
#         restricted_types = ["early_closing", "late_closing", "early_opening", "late_opening"]
#         if data.get("hours_type") in restricted_types:
#             if not data.get("reason") or not data.get("starting_date"):
#                 return JsonResponse(
#                     {"error": "For early_closing, late_closing, early_opening, late_opening 'reason' and 'starting_date' are required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             data.setdefault("schedule_with", "N/A")
#             data.setdefault("ages_allowed", "N/A")

#         if data.get("hours_type") == "special":
#             if not data.get("schedule_with") or not data.get("starting_date") or not data.get("ages_allowed"):
#                 return JsonResponse(
#                     {"error": "For special, 'ages_allowed' and 'starting_date' are required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )

#         if data.get("hours_type") == "closed":
#             if not data.get("starting_date") or not data.get("reason"):
#                 return JsonResponse(
#                     {"error": "For closed, 'starting_date' and 'reason' are required"},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
#             data.setdefault("schedule_with", "closed")
#             data.setdefault("ages_allowed", "closed")
#             data.setdefault("start_time", "00:00:00")
#             data.setdefault("end_time", "00:00:00")

#         # --- Multi-day 'special' (create one row per date in range) ---
#         if (data.get("hours_type") == "special" and
#             data.get("starting_date") and
#             data.get("ending_date") and
#             data["starting_date"] != data["ending_date"]):
#             # call the synchronous helper in a thread via sync_to_async
#             entries = await sync_to_async(create_date_range_entries)(data, same_entry_id)
#             # return the first created entry (or adapt as needed)
#             serializer = HoursOfOperationSerializer(entries[0])
#             return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

#         # --- Single-day entry (or special with same start/end) ---
#         # Prepare serializer with incoming data (we DO NOT rely on providing same_entry_id via input)
#         serializer = HoursOfOperationSerializer(data=data)
#         is_valid = await sync_to_async(serializer.is_valid)()
#         if not is_valid:
#             return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#         # pass server-generated same_entry_id into save() so it gets written despite read_only
#         instance = await sync_to_async(serializer.save)(same_entry_id=same_entry_id)

#         # Return the serialized instance
#         updated_serializer = HoursOfOperationSerializer(instance)
#         return JsonResponse(updated_serializer.data, status=status.HTTP_201_CREATED)

#     except Exception as e:
#         # keep logging for debugging
#         print("create_hours_of_operation error:", str(e))
#         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



# async def get_hours_of_operations(request, location_id):
#     try:
#         user, error_response = await require_admin(request)
#         if error_response:
#             return error_response
        
#         hours = await sync_to_async(lambda: list(HoursOfOperation.objects.filter(location_id=location_id).order_by('starting_date')))()
#         serializer = HoursOfOperationSerializer(hours, many=True)
#         return JsonResponse(serializer.data, safe=False, status=200)
    
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# async def update_hours_of_operation(request, location_id, pk):
#     try:
#         user, error_response = await require_admin(request)
#         if error_response:
#             return error_response
        
#         hours = await sync_to_async(HoursOfOperation.objects.get)(pk=pk, location_id=location_id)
        
#         body = await sync_to_async(request.body.decode)('utf-8')
#         data = json.loads(body)
#         data["location"] = location_id
        
#         restricted_types = ["special", "early_closing", "late_closing", "early_opening", "late_opening"]
#         if data.get("hours_type") in restricted_types:
#             if not data.get("reason") or not data.get("starting_date"):
#                 return JsonResponse(
#                     {"error": "For special/closing/opening hours, 'reason' and 'starting_date' are required."},
#                     status=status.HTTP_400_BAD_REQUEST
#                 )
        
#         # serializer = HoursOfOperationSerializer(hours, data=data)
#         # is_valid = await sync_to_async(serializer.is_valid)()
#         # if is_valid:
#         #     await sync_to_async(serializer.save)()
#         #     return JsonResponse(serializer.data, status=status.HTTP_200_OK)
                
#         serializer = HoursOfOperationSerializer(hours, data=data)
#         is_valid = await sync_to_async(serializer.is_valid)()
#         if is_valid:
#             instance = await sync_to_async(serializer.save)()
            
#             # If updating and same_entry_id is missing, preserve the existing one
#             if not instance.same_entry_id and hours.same_entry_id:
#                 instance.same_entry_id = hours.same_entry_id
#                 await sync_to_async(instance.save)()
            
#             updated_serializer = HoursOfOperationSerializer(instance)
#             return JsonResponse(updated_serializer.data, status=status.HTTP_200_OK)



#         print("This is the error:", serializer.errors)
#         return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
#     except HoursOfOperation.DoesNotExist:
#         return JsonResponse({"error": "Hours of Operation not found"}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# async def handle_group_split_after_delete(deleted_same_entry_id, location_id):
#     """Handle splitting of groups after deletion"""
#     try:
#         # Get all entries with the same same_entry_id
#         group_entries = await sync_to_async(list)(
#             HoursOfOperation.objects.filter(
#                 same_entry_id=deleted_same_entry_id, 
#                 location_id=location_id
#             ).order_by('starting_date')
#         )
        
#         if not group_entries:
#             return
        
#         # Group consecutive dates
#         groups = []
#         current_group = [group_entries[0]]
        
#         for i in range(1, len(group_entries)):
#             current_date = group_entries[i].starting_date
#             prev_date = group_entries[i-1].starting_date
            
#             if (current_date - prev_date).days == 1:
#                 current_group.append(group_entries[i])
#             else:
#                 groups.append(current_group)
#                 current_group = [group_entries[i]]
        
#         groups.append(current_group)
        
#         # If only one group remains, no need to split
#         if len(groups) <= 1:
#             return
        
#         # Assign new same_entry_id for each group (except the first one)
#         for group in groups[1:]:
#             new_same_entry_id = uuid.uuid4()
#             for entry in group:
#                 entry.same_entry_id = new_same_entry_id
#                 await sync_to_async(entry.save)()
    
#     except Exception as e:
#         print(f"Error in handle_group_split_after_delete: {str(e)}")

# async def delete_hours_of_operation(request, location_id, pk):
#     try:
#         user, error_response = await require_admin(request)
#         if error_response:
#             return error_response
        
#         hours = await sync_to_async(HoursOfOperation.objects.get)(pk=pk, location_id=location_id)
#         same_entry_id = hours.same_entry_id
        
#         await sync_to_async(hours.delete)()
        
#         # Handle group splitting after deletion
#         await handle_group_split_after_delete(same_entry_id, location_id)
        
#         return JsonResponse({"message": "Hours of Operation deleted successfully"}, status=200)
    
#     except HoursOfOperation.DoesNotExist:
#         return JsonResponse({"error": "Hours of Operation not found"}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)








# views.py - Updated with proper group splitting on individual deletion
import json
import uuid
from datetime import datetime, timedelta
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.hours_of_operations_model import HoursOfOperation
from myapp.serializers import HoursOfOperationSerializer

async def require_admin(request):
    try:
        user_auth_tuple = await sync_to_async(JWTAuthentication().authenticate)(request)
    except AuthenticationFailed as e:
        return None, JsonResponse({"detail": str(e)}, status=401)

    if not user_auth_tuple:
        return None, JsonResponse({"detail": "Authentication credentials were not provided."}, status=401)

    user, token = user_auth_tuple
    if not user.is_authenticated or not user.is_staff:
        return None, JsonResponse({"detail": "You do not have permission to perform this action."}, status=403)

    return user, None

def create_date_range_entries(data, same_entry_id):
    """
    Create multiple entries for date range with same same_entry_id
    Works for special, early_closing, late_closing, early_opening, late_opening, and closed types
    """
    entries = []
    start_date = datetime.strptime(data["starting_date"], "%Y-%m-%d").date()
    end_date = datetime.strptime(data["ending_date"], "%Y-%m-%d").date()

    current_date = start_date
    while current_date <= end_date:
        entry_data = data.copy()
        entry_data["starting_date"] = current_date.isoformat()
        entry_data["ending_date"] = current_date.isoformat()
        entry_data["starting_day_name"] = current_date.strftime("%A")
        entry_data["ending_day_name"] = current_date.strftime("%A")
        
        serializer = HoursOfOperationSerializer(data=entry_data)
        if serializer.is_valid():
            instance = serializer.save(same_entry_id=same_entry_id)
            entries.append(instance)
        else:
            raise Exception(f"Validation error for date {current_date}: {serializer.errors}")
        
        current_date += timedelta(days=1)
    
    return entries

async def create_hours_of_operation(request, location_id):
    """
    Async view for creating HoursOfOperation entries with multi-day support for all types
    """
    try:
        # auth
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        # parse body
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id

        # generate server-side same_entry_id
        same_entry_id = uuid.uuid4()

        # Define multi-day types
        multi_day_types = [
            "special", "early_closing", "late_closing", 
            "early_opening", "late_opening", "closed"
        ]

        # Validate required fields for restricted types early
        restricted_types = ["early_closing", "late_closing", "early_opening", "late_opening"]
        if data.get("hours_type") in restricted_types:
            if not data.get("reason") or not data.get("starting_date"):
                return JsonResponse(
                    {"error": "For early_closing, late_closing, early_opening, late_opening 'reason' and 'starting_date' are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data.setdefault("schedule_with", "")
            data.setdefault("ages_allowed", "")

        if data.get("hours_type") == "special":
            if not data.get("schedule_with") or not data.get("starting_date") or not data.get("ages_allowed"):
                return JsonResponse(
                    {"error": "For special, 'schedule_with', 'ages_allowed' and 'starting_date' are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if data.get("hours_type") == "closed":
            if not data.get("starting_date") or not data.get("reason"):
                return JsonResponse(
                    {"error": "For closed, 'starting_date' and 'reason' are required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data.setdefault("schedule_with", "closed")
            data.setdefault("ages_allowed", "closed")
            data.setdefault("start_time", "00:00:00")
            data.setdefault("end_time", "00:00:00")

        # --- Multi-day entries (create one row per date in range) ---
        # For all multi-day types, create multiple entries if start and end dates are different
        if (data.get("hours_type") in multi_day_types and
            data.get("starting_date") and
            data.get("ending_date") and
            data["starting_date"] != data["ending_date"]):
            
            # call the synchronous helper in a thread via sync_to_async
            entries = await sync_to_async(create_date_range_entries)(data, same_entry_id)
            # return the first created entry
            serializer = HoursOfOperationSerializer(entries[0])
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

        # --- Single-day entry ---
        # Prepare serializer with incoming data
        serializer = HoursOfOperationSerializer(data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if not is_valid:
            return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # pass server-generated same_entry_id into save()
        instance = await sync_to_async(serializer.save)(same_entry_id=same_entry_id)

        # Return the serialized instance
        updated_serializer = HoursOfOperationSerializer(instance)
        return JsonResponse(updated_serializer.data, status=status.HTTP_201_CREATED)

    except Exception as e:
        print("create_hours_of_operation error:", str(e))
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_hours_of_operations(request, location_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        hours = await sync_to_async(lambda: list(HoursOfOperation.objects.filter(location_id=location_id).order_by('starting_date')))()
        serializer = HoursOfOperationSerializer(hours, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_hours_of_operation(request, location_id, pk):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        hours = await sync_to_async(HoursOfOperation.objects.get)(pk=pk, location_id=location_id)
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id
        
        restricted_types = ["special", "early_closing", "late_closing", "early_opening", "late_opening"]
        if data.get("hours_type") in restricted_types:
            if not data.get("reason") or not data.get("starting_date"):
                return JsonResponse(
                    {"error": "For special/closing/opening hours, 'reason' and 'starting_date' are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        serializer = HoursOfOperationSerializer(hours, data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            instance = await sync_to_async(serializer.save)()
            
            # If updating and same_entry_id is missing, preserve the existing one
            if not instance.same_entry_id and hours.same_entry_id:
                instance.same_entry_id = hours.same_entry_id
                await sync_to_async(instance.save)()
            
            updated_serializer = HoursOfOperationSerializer(instance)
            return JsonResponse(updated_serializer.data, status=status.HTTP_200_OK)

        print("This is the error:", serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except HoursOfOperation.DoesNotExist:
        return JsonResponse({"error": "Hours of Operation not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

def handle_group_split_after_delete(deleted_same_entry_id, location_id, deleted_date=None):
    """
    Handle splitting of groups after individual day deletion
    If a middle date is deleted from a group, split the group into two separate groups
    """
    try:
        # Get all entries with the same same_entry_id, ordered by date
        group_entries = list(
            HoursOfOperation.objects.filter(
                same_entry_id=deleted_same_entry_id, 
                location_id=location_id
            ).order_by('starting_date')
        )
        
        if len(group_entries) <= 1:
            return
        
        # If we're deleting a specific date, find where it would have been
        if deleted_date:
            # Sort the entries to find consecutive date ranges
            entries_sorted = sorted(group_entries, key=lambda x: x.starting_date)
            
            # Find consecutive date ranges
            ranges = []
            current_range = [entries_sorted[0]]
            
            for i in range(1, len(entries_sorted)):
                current_entry = entries_sorted[i]
                prev_entry = entries_sorted[i-1]
                
                # Check if dates are consecutive
                if (current_entry.starting_date - prev_entry.starting_date).days == 1:
                    current_range.append(current_entry)
                else:
                    ranges.append(current_range)
                    current_range = [current_entry]
            
            ranges.append(current_range)
            
            # If we have more than one range after processing, assign new same_entry_id to each range
            if len(ranges) > 1:
                for range_entries in ranges:
                    new_same_entry_id = uuid.uuid4()
                    for entry in range_entries:
                        entry.same_entry_id = new_same_entry_id
                        entry.save()
        
    except Exception as e:
        print(f"Error in handle_group_split_after_delete: {str(e)}")

async def delete_hours_of_operation(request, location_id, pk):
    """
    Delete hours of operation with proper group handling
    - If deleting from main group button: delete entire group
    - If deleting individual day: delete only that day and split group if needed
    """
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        # Get the hour to be deleted
        hour_to_delete = await sync_to_async(HoursOfOperation.objects.get)(pk=pk, location_id=location_id)
        same_entry_id = hour_to_delete.same_entry_id
        deleted_date = hour_to_delete.starting_date
        
        # Check if this is a group deletion (delete_group parameter)
        delete_group = request.GET.get('delete_group', 'false').lower() == 'true'
        
        if delete_group and same_entry_id:
            # Delete all entries with the same same_entry_id (entire group)
            group_entries = await sync_to_async(list)(
                HoursOfOperation.objects.filter(
                    same_entry_id=same_entry_id, 
                    location_id=location_id
                )
            )
            # Delete all entries in the group
            for entry in group_entries:
                await sync_to_async(entry.delete)()
            message = f"Deleted entire group ({len(group_entries)} entries) successfully"
        else:
            # Single entry deletion - delete only this entry
            await sync_to_async(hour_to_delete.delete)()
            message = "Hours entry deleted successfully"
            
            # If this was part of a group, handle group splitting
            if same_entry_id:
                await sync_to_async(handle_group_split_after_delete)(same_entry_id, location_id, deleted_date)
        
        return JsonResponse({"message": message}, status=200)
    
    except HoursOfOperation.DoesNotExist:
        return JsonResponse({"error": "Hours of Operation not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

