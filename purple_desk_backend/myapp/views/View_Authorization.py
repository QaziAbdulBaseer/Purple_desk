from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated


from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAdminUser
from myapp.models import User

from myapp.serializers import RegisterSerializer , UserSerializer




# ---------------------------
# Signup (Register)
# ---------------------------
@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                'id': user.id,
                'username': user.username,
                'role': user.role
            },
            status=status.HTTP_201_CREATED
        )
    print("This is the error:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------
# Custom JWT login (with role + username in token)
# ---------------------------
# @api_view(['POST'])
# @permission_classes([AllowAny])
# def token_obtain_pair_view(request):
#     from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

#     serializer = TokenObtainPairSerializer(data=request.data)
#     if serializer.is_valid():
#         user = User.objects.get(username=request.data['username'])
#         refresh = RefreshToken.for_user(user)
#         refresh['role'] = user.role
#         refresh['username'] = user.username

#         # return Response({
#         #     'refresh': str(refresh),
#         #     'access': str(refresh.access_token),
#         # }, status=status.HTTP_200_OK)
#         return Response({
#             'refresh': str(refresh),
#             'access': str(refresh.access_token),
#             'username': user.username,
#             'role': user.role
#         }, status=status.HTTP_200_OK)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




# In your token_obtain_pair_view function
@api_view(['POST'])
@permission_classes([AllowAny])
def token_obtain_pair_view(request):
    from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

    serializer = TokenObtainPairSerializer(data=request.data)
    if serializer.is_valid():
        user = User.objects.get(username=request.data['username'])
        refresh = RefreshToken.for_user(user)
        refresh['role'] = user.role
        refresh['username'] = user.username

        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'userData': {  # Add user data to response
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role
            }
        }, status=status.HTTP_200_OK)
    print("This is the error:", serializer.errors)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ---------------------------
# Profile (Protected endpoint)
# ---------------------------
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    user = request.user
    return Response({
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'role': user.role
    }, status=status.HTTP_200_OK)



@api_view(['GET'])
@permission_classes([IsAdminUser])   # ✅ only superusers allowed
def user_list(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)