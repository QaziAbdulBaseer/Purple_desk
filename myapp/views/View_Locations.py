import json
from django.http import JsonResponse
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework import status
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.locations_model import Location
from myapp.serializers import LocationSerializer


# --- Auth helper ---
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


# --- CRUD Views ---

# CREATE
async def create_location(request):
    user, error_response = await require_admin(request)
    if error_response:
        return error_response

    body = await sync_to_async(request.body.decode)()
    data = json.loads(body)

    serializer = LocationSerializer(data=data)
    is_valid = await sync_to_async(serializer.is_valid)()
    if is_valid:
        await sync_to_async(serializer.save)()
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
    print("This is the error:", serializer.errors)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# READ ALL
async def get_locations(request):
    user, error_response = await require_admin(request)
    if error_response:
        return error_response

    locations = await sync_to_async(lambda: list(Location.objects.all()))()
    serializer = LocationSerializer(locations, many=True)
    return JsonResponse(serializer.data, safe=False, status=status.HTTP_200_OK)


# READ ONE
async def get_location(request, pk):
    user, error_response = await require_admin(request)
    if error_response:
        return error_response

    try:
        location = await sync_to_async(Location.objects.get)(pk=pk)
    except Location.DoesNotExist:
        return JsonResponse({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    serializer = LocationSerializer(location)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)


# UPDATE
async def update_location(request, pk):
    user, error_response = await require_admin(request)
    if error_response:
        return error_response

    try:
        location = await sync_to_async(Location.objects.get)(pk=pk)
    except Location.DoesNotExist:
        return JsonResponse({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    body = request.body.decode()
    data = json.loads(body)

    serializer = LocationSerializer(location, data=data)
    is_valid = await sync_to_async(serializer.is_valid)()
    if is_valid:
        await sync_to_async(serializer.save)()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    print("This is the error:", serializer.errors)
    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# DELETE
async def delete_location(request, pk):
    user, error_response = await require_admin(request)
    if error_response:
        return error_response

    try:
        location = await sync_to_async(Location.objects.get)(pk=pk)
    except Location.DoesNotExist:
        return JsonResponse({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    await sync_to_async(location.delete)()
    return JsonResponse({"message": "Location deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
