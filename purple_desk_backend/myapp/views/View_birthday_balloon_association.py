


# views_birthday_balloon_association.py
import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from asgiref.sync import sync_to_async

from myapp.model.birthday_balloon_association_model import BirthdayBalloonPackageAssociation
from myapp.model.birthday_party_packages_model import BirthdayPartyPackage
from myapp.model.party_balloon_Packages import PartyBalloonPackage
from myapp.serializers import (
    BirthdayBalloonPackageAssociationSerializer,
    BirthdayBalloonPackageAssociationCreateSerializer,
    PartyBalloonPackageSerializer,
)

# ---------------------------------------------------------------------
# ✅ Helper: Authentication + Admin Check
# ---------------------------------------------------------------------
async def require_admin(request):
    """Ensure the user is authenticated and is an admin."""
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

# ---------------------------------------------------------------------
# ✅ Create Association
# ---------------------------------------------------------------------
async def create_birthday_party_balloon_package(request, location_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        body = await sync_to_async(request.body.decode)("utf-8")
        data = json.loads(body)
        data["location"] = location_id

        # Use sync_to_async for the database operations
        @sync_to_async
        def create_association():
            serializer = BirthdayBalloonPackageAssociationCreateSerializer(data=data)
            if serializer.is_valid():
                serializer.save()
                full_serializer = BirthdayBalloonPackageAssociationSerializer(serializer.instance)
                return full_serializer.data, None
            return None, serializer.errors

        created_data, errors = await create_association()
        if created_data:
            return JsonResponse(created_data, status=201)
        return JsonResponse(errors, status=400)

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ---------------------------------------------------------------------
# ✅ Get All Associations for a Location
# ---------------------------------------------------------------------
async def get_birthday_party_balloon_packages(request, location_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        @sync_to_async
        def get_associations():
            packages = BirthdayBalloonPackageAssociation.objects.filter(location_id=location_id)\
                .select_related('birthday_party_package', 'party_balloon_package')
            serializer = BirthdayBalloonPackageAssociationSerializer(packages, many=True)
            return serializer.data

        data = await get_associations()
        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ---------------------------------------------------------------------
# ✅ Get Associations for Specific Birthday Package
# ---------------------------------------------------------------------
async def get_birthday_party_balloon_packages_by_birthday_package(request, location_id, birthday_package_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        @sync_to_async
        def get_associations():
            packages = BirthdayBalloonPackageAssociation.objects.filter(
                location_id=location_id,
                birthday_party_package_id=birthday_package_id
            ).select_related('birthday_party_package', 'party_balloon_package')
            serializer = BirthdayBalloonPackageAssociationSerializer(packages, many=True)
            return serializer.data

        data = await get_associations()
        return JsonResponse(data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ---------------------------------------------------------------------
# ✅ Get Available (Unassociated) Balloon Packages
# ---------------------------------------------------------------------
async def get_available_balloon_packages_for_birthday_package(request, location_id, birthday_package_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        @sync_to_async
        def get_available_balloons():
            # Get already associated balloon package IDs
            associated_ids = list(
                BirthdayBalloonPackageAssociation.objects.filter(
                    location_id=location_id,
                    birthday_party_package_id=birthday_package_id
                ).values_list('party_balloon_package_id', flat=True)
            )
            
            # Get unassociated balloon packages
            available_balloons = PartyBalloonPackage.objects.filter(location_id=location_id)\
                .exclude(party_balloon_package_id__in=associated_ids)
            
            serializer = PartyBalloonPackageSerializer(available_balloons, many=True)
            return serializer.data

        data = await get_available_balloons()
        return JsonResponse(data, safe=False, status=200)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ---------------------------------------------------------------------
# ✅ Get Single Association
# ---------------------------------------------------------------------
async def get_birthday_party_balloon_package(request, location_id, pk):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        @sync_to_async
        def get_association():
            package = BirthdayBalloonPackageAssociation.objects.get(
                birthday_party_balloon_id=pk,
                location_id=location_id
            )
            serializer = BirthdayBalloonPackageAssociationSerializer(package)
            return serializer.data

        data = await get_association()
        return JsonResponse(data, status=200)
    except BirthdayBalloonPackageAssociation.DoesNotExist:
        return JsonResponse({"error": "Association not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ---------------------------------------------------------------------
# ✅ Update Association
# ---------------------------------------------------------------------
async def update_birthday_party_balloon_package(request, location_id, pk):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        body = await sync_to_async(request.body.decode)("utf-8")
        data = json.loads(body)
        data["location"] = location_id

        @sync_to_async
        def update_association():
            package = BirthdayBalloonPackageAssociation.objects.get(
                birthday_party_balloon_id=pk, 
                location_id=location_id
            )
            serializer = BirthdayBalloonPackageAssociationCreateSerializer(package, data=data)
            if serializer.is_valid():
                serializer.save()
                full_serializer = BirthdayBalloonPackageAssociationSerializer(serializer.instance)
                return full_serializer.data, None
            return None, serializer.errors

        updated_data, errors = await update_association()
        if updated_data:
            return JsonResponse(updated_data, status=200)
        return JsonResponse(errors, status=400)

    except BirthdayBalloonPackageAssociation.DoesNotExist:
        return JsonResponse({"error": "Association not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)

# ---------------------------------------------------------------------
# ✅ Delete Association
# ---------------------------------------------------------------------
async def delete_birthday_party_balloon_package(request, location_id, pk):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        @sync_to_async
        def delete_association():
            package = BirthdayBalloonPackageAssociation.objects.get(
                birthday_party_balloon_id=pk,
                location_id=location_id
            )
            package.delete()

        await delete_association()
        return JsonResponse({"message": "Association deleted successfully"}, status=200)

    except BirthdayBalloonPackageAssociation.DoesNotExist:
        return JsonResponse({"error": "Association not found"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)