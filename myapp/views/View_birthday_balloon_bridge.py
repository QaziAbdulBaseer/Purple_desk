


import json
from django.http import JsonResponse
from rest_framework import status
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.birthday_party_packages_model import BirthdayPartyPackage
from myapp.model.balloon_party_packages_model import BalloonPartyPackage
from myapp.model.birthday_balloon_bridge_model import BirthdayBalloonBridge
from myapp.serializers import (
    BirthdayBalloonBridgeSerializer, 
    BirthdayPackageWithBalloonsSerializer
) 

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

# GET all balloon packages for a specific birthday package
async def get_birthday_package_balloons(request, location_id, birthday_package_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        @sync_to_async
        def get_birthday_package_with_balloons():
            birthday_package = BirthdayPartyPackage.objects.get(
                pk=birthday_package_id, 
                location_id=location_id
            )
            serializer = BirthdayPackageWithBalloonsSerializer(birthday_package)

            return serializer.data
        
        data = await get_birthday_package_with_balloons()
        return JsonResponse(data, safe=False, status=200)
    
    except BirthdayPartyPackage.DoesNotExist:
        return JsonResponse({"error": "Birthday Party Package not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ADD balloon package to birthday package
async def add_balloon_to_birthday_package(request, location_id, birthday_package_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        body = await sync_to_async(lambda: request.body.decode('utf-8'))()
        data = json.loads(body)
        balloon_package_id = data.get('balloon_package_id')

        if not balloon_package_id:
            return JsonResponse({"error": "balloon_package_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        @sync_to_async
        def add_balloon_association():
            try:
                birthday_package = BirthdayPartyPackage.objects.get(
                    pk=birthday_package_id, 
                    location_id=location_id
                )
                balloon_package = BalloonPartyPackage.objects.get(
                    pk=balloon_package_id, 
                    location_id=location_id
                )

                if BirthdayBalloonBridge.objects.filter(
                    birthday_party_package=birthday_package,
                    balloon_party_package=balloon_package
                ).exists():
                    return None, "This balloon package is already associated with the birthday package"

                bridge_data = {
                    'birthday_party_package': birthday_package.birthday_party_packages_id,
                    'balloon_party_package': balloon_package.balloon_party_packages_id,
                    'is_active': True
                }
                serializer = BirthdayBalloonBridgeSerializer(data=bridge_data)

                if serializer.is_valid():
                    instance = serializer.save()
                    return instance, None
                return None, serializer.errors


                if serializer.is_valid():
                    instance = serializer.save()
                    return instance, None
                return None, serializer.errors

            except BirthdayPartyPackage.DoesNotExist:
                return None, "Birthday Party Package not found"
            except BalloonPartyPackage.DoesNotExist:
                return None, "Balloon Party Package not found"

        instance, error = await add_balloon_association()
        
        if instance:
            updated_serializer = BirthdayBalloonBridgeSerializer(instance)
            return JsonResponse(updated_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse({"error": error}, status=status.HTTP_400_BAD_REQUEST)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# REMOVE balloon package from birthday package
async def remove_balloon_from_birthday_package(request, location_id, birthday_package_id, balloon_package_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        @sync_to_async
        def remove_balloon_association():
            try:
                bridge_relation = BirthdayBalloonBridge.objects.get(
                    birthday_party_package_id=birthday_package_id,
                    balloon_party_package_id=balloon_package_id
                )
                bridge_relation.delete()
                return True, None
            except BirthdayBalloonBridge.DoesNotExist:
                return False, "Balloon package is not associated with this birthday package"

        success, error = await remove_balloon_association()
        
        if success:
            return JsonResponse({"message": "Balloon package removed from birthday package successfully"}, status=200)
        else:
            return JsonResponse({"error": error}, status=status.HTTP_404_NOT_FOUND)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)