# myapp/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from myapp.model.locations_model import Location
from myapp.serializers import LocationSerializer

# # CREATE
# @api_view(['POST'])
# @permission_classes([IsAdminUser])   # ✅ only admins
# def create_location(request):
#     serializer = LocationSerializer(data=request.data)
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



@api_view(['POST'])
@permission_classes([IsAdminUser])   # ✅ only admins
def create_location(request):
    location_name = request.data.get('location_name')

    # Check if location with same name already exists
    if Location.objects.filter(location_name=location_name).exists():
        return Response(
            {"error": f"Location '{location_name}' already exists."},
            status=status.HTTP_400_BAD_REQUEST
        )

    serializer = LocationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
# READ (single + list)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_locations(request):
    locations = Location.objects.all()
    serializer = LocationSerializer(locations, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes([IsAdminUser])
def get_location(request, pk):
    try:
        location = Location.objects.get(pk=pk)
    except Location.DoesNotExist:
        return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = LocationSerializer(location)
    return Response(serializer.data, status=status.HTTP_200_OK)

# UPDATE
@api_view(['PUT'])
@permission_classes([IsAdminUser])
def update_location(request, pk):
    try:
        location = Location.objects.get(pk=pk)
    except Location.DoesNotExist:
        return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)
    serializer = LocationSerializer(location, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# DELETE
@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_location(request, pk):
    try:
        location = Location.objects.get(pk=pk)
    except Location.DoesNotExist:
        return Response({"error": "Location not found"}, status=status.HTTP_404_NOT_FOUND)
    location.delete()
    return Response({"message": "Location deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
