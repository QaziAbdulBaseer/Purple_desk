


import json
from django.http import JsonResponse
from rest_framework import status
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.balloon_party_packages_model import BalloonPartyPackage
from myapp.serializers import BalloonPartyPackageSerializer

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

# GET all balloon packages for a location
async def get_balloon_party_packages(request, location_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        balloon_packages = await sync_to_async(list)(
            BalloonPartyPackage.objects.filter(location_id=location_id).order_by('call_flow_priority')
        )
        serializer = BalloonPartyPackageSerializer(balloon_packages, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# GET single balloon package
async def get_balloon_party_package(request, location_id, pk):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        balloon_package = await sync_to_async(BalloonPartyPackage.objects.get)(
            pk=pk, 
            location_id=location_id
        )
        serializer = BalloonPartyPackageSerializer(balloon_package)
        return JsonResponse(serializer.data, safe=False, status=200)
    
    except BalloonPartyPackage.DoesNotExist:
        return JsonResponse({"error": "Balloon Party Package not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# CREATE balloon package
async def create_balloon_party_package(request, location_id):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        body = await sync_to_async(lambda: request.body.decode('utf-8'))()
        data = json.loads(body)
        data["location"] = location_id

        @sync_to_async
        def create_balloon_package():
            serializer = BalloonPartyPackageSerializer(data=data)
            if serializer.is_valid():
                instance = serializer.save()
                return instance, None
            return None, serializer.errors

        instance, errors = await create_balloon_package()
        
        if instance:
            updated_serializer = BalloonPartyPackageSerializer(instance)
            return JsonResponse(updated_serializer.data, status=status.HTTP_201_CREATED)
        else:
            return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST)
    
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# UPDATE balloon package
async def update_balloon_party_package(request, location_id, pk):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        balloon_package = await sync_to_async(BalloonPartyPackage.objects.get)(
            pk=pk, 
            location_id=location_id
        )
        
        body = await sync_to_async(lambda: request.body.decode('utf-8'))()
        data = json.loads(body)
        data["location"] = location_id

        @sync_to_async
        def update_balloon_package():
            serializer = BalloonPartyPackageSerializer(balloon_package, data=data)
            if serializer.is_valid():
                instance = serializer.save()
                return instance, None
            return None, serializer.errors

        instance, errors = await update_balloon_package()
        
        if instance:
            updated_serializer = BalloonPartyPackageSerializer(instance)
            return JsonResponse(updated_serializer.data, status=status.HTTP_200_OK)
        else:
            return JsonResponse(errors, status=status.HTTP_400_BAD_REQUEST)
    
    except BalloonPartyPackage.DoesNotExist:
        return JsonResponse({"error": "Balloon Party Package not found"}, status=status.HTTP_404_NOT_FOUND)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# DELETE balloon package
async def delete_balloon_party_package(request, location_id, pk):
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        balloon_package = await sync_to_async(BalloonPartyPackage.objects.get)(
            pk=pk, 
            location_id=location_id
        )
        await sync_to_async(balloon_package.delete)()
        return JsonResponse({"message": "Balloon Party Package deleted successfully"}, status=200)
    
    except BalloonPartyPackage.DoesNotExist:
        return JsonResponse({"error": "Balloon Party Package not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)