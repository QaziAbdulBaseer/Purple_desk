import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.birthday_party_packages_model import BirthdayPartyPackage
from myapp.serializers import BirthdayPartyPackageSerializer

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

async def create_birthday_party_package(request, location_id):
    """Create a new birthday party package for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # attach FK
        
        serializer = BirthdayPartyPackageSerializer(data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        print("This is the error:", serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @permission_classes([IsAdminUser])
async def get_birthday_party_packages(request, location_id):
    """Get all birthday party packages for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        packages = await sync_to_async(lambda: list(
            BirthdayPartyPackage.objects.filter(location_id=location_id)
        ))()
        serializer = BirthdayPartyPackageSerializer(packages, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @permission_classes([IsAdminUser])
async def get_birthday_party_package(request, location_id, pk):
    """Get a specific birthday party package by its primary key and location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        package = await sync_to_async(BirthdayPartyPackage.objects.get)(
            birthday_party_packages_id=pk, location_id=location_id
        )
        serializer = BirthdayPartyPackageSerializer(package)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    except BirthdayPartyPackage.DoesNotExist:
        return JsonResponse(
            {"error": "Birthday party package not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @permission_classes([IsAdminUser])
async def update_birthday_party_package(request, location_id, pk):
    """Update a birthday party package"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        package = await sync_to_async(BirthdayPartyPackage.objects.get)(
            birthday_party_packages_id=pk, location_id=location_id
        )
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # keep FK intact
        
        serializer = BirthdayPartyPackageSerializer(package, data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        print("This is the error:", serializer.errors)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except BirthdayPartyPackage.DoesNotExist:
        return JsonResponse(
            {"error": "Birthday party package not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# @permission_classes([IsAdminUser])
async def delete_birthday_party_package(request, location_id, pk):
    """Delete a birthday party package"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        package = await sync_to_async(BirthdayPartyPackage.objects.get)(
            birthday_party_packages_id=pk, location_id=location_id
        )
        await sync_to_async(package.delete)()
        
        return JsonResponse(
            {"message": "Birthday party package deleted successfully"}, 
            status=200
        )
    except BirthdayPartyPackage.DoesNotExist:
        return JsonResponse(
            {"error": "Birthday party package not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)