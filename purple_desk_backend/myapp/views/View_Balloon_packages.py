

import json
from django.http import JsonResponse
from rest_framework import status
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.party_balloon_Packages import PartyBalloonPackage
from myapp.serializers import PartyBalloonPackageSerializer


# ============================================================
# ✅ AUTHENTICATION (Sync-safe wrapper)
# ============================================================

def require_admin_sync(request):
    """Synchronous admin check (wrapped safely for async)"""
    try:
        auth = JWTAuthentication()
        user_auth_tuple = auth.authenticate(request)
    except AuthenticationFailed as e:
        return None, JsonResponse({"detail": str(e)}, status=401)

    if not user_auth_tuple:
        return None, JsonResponse(
            {"detail": "Authentication credentials were not provided."}, status=401
        )

    user, token = user_auth_tuple
    if not user.is_authenticated or not user.is_staff:
        return None, JsonResponse(
            {"detail": "You do not have permission to perform this action."}, status=403
        )

    return user, None


async def require_admin(request):
    """Async wrapper for admin authentication"""
    return await sync_to_async(require_admin_sync)(request)


# ============================================================
# ✅ CREATE PACKAGE
# ============================================================

async def create_party_balloon_package(request, location_id):
    """Create a new party balloon package for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        # Decode request body
        body = await sync_to_async(request.body.decode)("utf-8")
        data = json.loads(body)
        data["location"] = location_id  # attach FK

        # Serializer operations are sync
        @sync_to_async
        def save_package():
            serializer = PartyBalloonPackageSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                return serializer.data, None
            return None, serializer.errors

        result, errors = await save_package()
        if errors:
            print("Serializer error:", errors)
            return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(result, status=status.HTTP_201_CREATED)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================
# ✅ GET ALL PACKAGES
# ============================================================

async def get_party_balloon_packages(request, location_id):
    """Get all party balloon packages for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        @sync_to_async
        def fetch_packages():
            packages = PartyBalloonPackage.objects.filter(location_id=location_id)
            serializer = PartyBalloonPackageSerializer(packages, many=True)
            return serializer.data

        data = await fetch_packages()
        return JsonResponse(data, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================
# ✅ GET SINGLE PACKAGE
# ============================================================

async def get_party_balloon_package(request, location_id, pk):
    """Get a specific party balloon package by its primary key and location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        @sync_to_async
        def fetch_package():
            package = PartyBalloonPackage.objects.get(
                party_balloon_package_id=pk, location_id=location_id
            )
            serializer = PartyBalloonPackageSerializer(package)
            return serializer.data

        data = await fetch_package()
        return JsonResponse(data, status=status.HTTP_200_OK)

    except PartyBalloonPackage.DoesNotExist:
        return JsonResponse(
            {"error": "Party balloon package not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================
# ✅ UPDATE PACKAGE
# ============================================================

async def update_party_balloon_package(request, location_id, pk):
    """Update a party balloon package"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        body = await sync_to_async(request.body.decode)("utf-8")
        data = json.loads(body)
        data["location"] = location_id

        @sync_to_async
        def update_package():
            package = PartyBalloonPackage.objects.get(
                party_balloon_package_id=pk, location_id=location_id
            )
            serializer = PartyBalloonPackageSerializer(package, data=data)
            if serializer.is_valid():
                serializer.save()
                return serializer.data, None
            return None, serializer.errors

        result, errors = await update_package()
        if errors:
            print("Serializer error:", errors)
            return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(result, status=status.HTTP_200_OK)

    except PartyBalloonPackage.DoesNotExist:
        return JsonResponse(
            {"error": "Party balloon package not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============================================================
# ✅ DELETE PACKAGE
# ============================================================

async def delete_party_balloon_package(request, location_id, pk):
    """Delete a party balloon package"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        @sync_to_async
        def delete_package():
            package = PartyBalloonPackage.objects.get(
                party_balloon_package_id=pk, location_id=location_id
            )
            package.delete()

        await delete_package()
        return JsonResponse({"message": "Party balloon package deleted successfully"}, status=200)

    except PartyBalloonPackage.DoesNotExist:
        return JsonResponse(
            {"error": "Party balloon package not found"}, status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)





## this is the sample code just for the referance. 