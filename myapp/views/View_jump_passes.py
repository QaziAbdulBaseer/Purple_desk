import json
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAdminUser
from asgiref.sync import sync_to_async
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from myapp.model.jump_passes_model import JumpPass
from myapp.serializers import JumpPassSerializer

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

async def create_jump_pass(request, location_id):
    """Create a new jump pass for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # attach FK
        
        serializer = JumpPassSerializer(data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_201_CREATED)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def get_jump_passes(request, location_id):
    """Get all jump passes for a specific location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        jump_passes = await sync_to_async(lambda: list(
            JumpPass.objects.filter(location_id=location_id)
        ))()
        serializer = JumpPassSerializer(jump_passes, many=True)
        return JsonResponse(serializer.data, safe=False, status=200)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def get_jump_pass(request, location_id, pk):
    """Get a specific jump pass by its primary key and location"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response

        jump_pass = await sync_to_async(JumpPass.objects.get)(
            jump_pass_id=pk, location_id=location_id
        )
        serializer = JumpPassSerializer(jump_pass)
        return JsonResponse(serializer.data, status=status.HTTP_200_OK)
    except JumpPass.DoesNotExist:
        return JsonResponse(
            {"error": "Jump pass not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def update_jump_pass(request, location_id, pk):
    """Update a jump pass"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        jump_pass = await sync_to_async(JumpPass.objects.get)(
            jump_pass_id=pk, location_id=location_id
        )
        
        body = await sync_to_async(request.body.decode)('utf-8')
        data = json.loads(body)
        data["location"] = location_id   # keep FK intact
        
        serializer = JumpPassSerializer(jump_pass, data=data)
        is_valid = await sync_to_async(serializer.is_valid)()
        if is_valid:
            await sync_to_async(serializer.save)()
            return JsonResponse(serializer.data, status=status.HTTP_200_OK)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except JumpPass.DoesNotExist:
        return JsonResponse(
            {"error": "Jump pass not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


async def delete_jump_pass(request, location_id, pk):
    """Delete a jump pass"""
    try:
        user, error_response = await require_admin(request)
        if error_response:
            return error_response
        
        jump_pass = await sync_to_async(JumpPass.objects.get)(
            jump_pass_id=pk, location_id=location_id
        )
        await sync_to_async(jump_pass.delete)()
        
        return JsonResponse(
            {"message": "Jump pass deleted successfully"}, 
            status=200
        )
    except JumpPass.DoesNotExist:
        return JsonResponse(
            {"error": "Jump pass not found"}, 
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)