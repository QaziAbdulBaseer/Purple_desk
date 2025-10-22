import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.hours_of_operations_model import HoursOfOperation
from myapp.serializers import HoursOfOperationSerializer
from django.http import HttpResponse



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



async def create_hours_of_operation(request, location_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # attach FK
        
        restricted_types = ["early_closing", "late_closing", "early_opening", "late_opening"]
        if data.get("hours_type") in restricted_types:
            if not data.get("reason") or not data.get("starting_date"):
                return JsonResponse(
                    {"error": "For early_closing, late_closing, early_opening, late_opening 'reason' and 'starting_date' are required."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data.setdefault("schedule_with", "N/A")
            data.setdefault("ages_allowed", "N/A")
        if data.get("hours_type") == "special":
            if not data.get("schedule_with") or not data.get("starting_date") or not data.get("ages_allowed"):
                return JsonResponse(
                    {"error": "For special, 'ages allowed' and 'starting_date' is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        if data.get("hours_type") == "closed":
            if not data.get("starting_date") or not data.get("reason"):
                return JsonResponse(
                    {"error": "For closed, 'starting' and 'reason' is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            data.setdefault("schedule_with", "closed")
            data.setdefault("ages_allowed", "closed")
            data.setdefault("start_time", "00:00:00")
            data.setdefault("end_time", "00:00:00")
        
        serializer = HoursOfOperationSerializer(data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        print("This is the error:", serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print("This is the error:", str(e))
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def get_hours_of_operations(request, location_id):
    try:
        # Fixed: Use JsonResponse instead of manual HttpResponse + json.dumps
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        hours = await sync_to_async(lambda: list(HoursOfOperation.objects.filter(location_id=location_id)))()
        serializer = HoursOfOperationSerializer(hours, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @permission_classes([IsAdminUser])
# async def get_hours_of_operation(request, location_id, pk):
#     try:
#         hours = await sync_to_async(HoursOfOperation.objects.get)(pk=pk, location_id=location_id)
#         serializer = HoursOfOperationSerializer(hours)
#         return JsonResponse(serializer.data, status=status.HTTP_200_OK)
#     except HoursOfOperation.DoesNotExist:
#         return JsonResponse({"error": "Hours of Operation not found"}, status=status.HTTP_404_NOT_FOUND)
#     except Exception as e:
#         return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def update_hours_of_operation(request, location_id, pk):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        hours = await sync_to_async(HoursOfOperation.objects.get)(pk=pk, location_id=location_id)
        
        # Fixed: Make body decoding async
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # keep FK intact
        
        # custom validation
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
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        print("This is the error:", serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except HoursOfOperation.DoesNotExist:
        return JsonResponse({"error": "Hours of Operation not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

async def delete_hours_of_operation(request, location_id, pk):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        hours = await sync_to_async(HoursOfOperation.objects.get)(pk=pk, location_id=location_id)
        await sync_to_async(hours.delete)()
        
        # Fixed: Use JsonResponse instead of manual HttpResponse
        # Note: 204 No Content should not have a response body, but if you need a message, use 200
        return JsonResponse({"message": "Hours of Operation deleted successfully"}, status=200)
        
        # OR for proper 204 No Content (no body):
        # return HttpResponse(status=204)
    except HoursOfOperation.DoesNotExist:
        return JsonResponse({"error": "Hours of Operation not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    