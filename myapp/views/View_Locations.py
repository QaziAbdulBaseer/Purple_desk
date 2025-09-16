# myapp/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from asgiref.sync import sync_to_async
from rest_framework.permissions import IsAdminUser
from myapp.model.locations_model import Location
from myapp.serializers import LocationSerializer
import json
from django.utils.decorators import method_decorator

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import asyncio
from django.views.decorators.csrf import ensure_csrf_cookie

# @csrf_exempt

@ensure_csrf_cookie
def get_csrf(request):
    return JsonResponse({"detail": "CSRF cookie set"})


@permission_classes([IsAdminUser])   # ✅ only admins
async def create_location(request):
    body = await sync_to_async(request.body.decode)()  # get raw body
    data = json.loads(body)
    location_name = data.get('location_name')

    # Run ORM queries in a thread
    exists = await sync_to_async(Location.objects.filter(location_name=location_name).exists)()
    if exists:
        return JsonResponse(
            {"error": f"Location '{location_name}' already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = LocationSerializer(data=data)

    is_valid = await sync_to_async(serializer.is_valid)()
    if is_valid:
        # save() also calls ORM -> wrap in sync_to_async
        await sync_to_async(serializer.save)()
        return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@permission_classes([IsAdminUser])
async def get_locations(request):
    locations = await sync_to_async(lambda: list(Location.objects.all()))()
    serializer = LocationSerializer(locations, many=True)
    return JsonResponse(serializer.data, safe=False, status=200)


@permission_classes([IsAdminUser])
async def get_location(request, pk):
    try:
        location = await sync_to_async(lambda: Location.objects.get(pk=pk))()
        # location = Location.objects.get(pk=pk)
    except Location.DoesNotExist:
        return JsonResponse({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = LocationSerializer(location)
    return JsonResponse(serializer.data, status=status.HTTP_200_OK)

# # UPDATE
@permission_classes([IsAdminUser])
async def update_location(request, pk):
    try:
        # ✅ ORM must run in thread
        location = await sync_to_async(Location.objects.get)(pk=pk)
    except Location.DoesNotExist:
        return JsonResponse({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    # ✅ Parse JSON body
    body = request.body.decode()
    data = json.loads(body)

    serializer = LocationSerializer(location, data=data)

    # ✅ Run serializer.is_valid in thread
    is_valid = await sync_to_async(serializer.is_valid)()
    if is_valid:
        # ✅ Run save() in thread
        await sync_to_async(serializer.save)()
        return JsonResponse(serializer.data, status=status.HTTP_200_OK, safe=False)

    return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST, safe=False)

# DELETE
@permission_classes([IsAdminUser])
async def delete_location(request, pk):
    try:
        # ✅ ORM lookup in a thread
        location = await sync_to_async(Location.objects.get)(pk=pk)
    except Location.DoesNotExist:
        return JsonResponse({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)

    # ✅ ORM delete in a thread
    await sync_to_async(location.delete)()

    return JsonResponse(
        {"message": "Location deleted successfully"},
        status=status.HTTP_204_NO_CONTENT
    )