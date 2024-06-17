from django.contrib.auth import authenticate
from django.contrib.auth.models import update_last_login
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.core.exceptions import ValidationError
from oauth2_provider.models import AccessToken, Application, RefreshToken
from oauth2_provider.settings import oauth2_settings
from oauthlib.common import generate_token
from .models import User, FriendRequest
from .serializers import UserSerializer, FriendRequestSerializer
from datetime import timedelta
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from django.db.models import Q
from .validators import validate_email, validate_password


class WelcomeView(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        return Response({'message': 'Welcome to social network.'}, status=status.HTTP_200_OK)
    
class SignUpView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        data = request.data
        email = data.get('email')
        password = data.get('password')
        try:
            validate_email(email)
            validate_password(password)
            user = User.objects.create_user(
                username=data['email'],
                email=data['email'],
                password=data['password']
            )
            return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
        except ValidationError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    permission_classes = [AllowAny]
    def post(self, request):
        email = request.data.get('email').lower()
        password = request.data.get('password')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            try:
                app = Application.objects.get(name='My Social Network App')
            except Application.DoesNotExist:
                return Response({'error': 'OAuth2 application not found'}, status=status.HTTP_400_BAD_REQUEST)

            token = generate_token()
            refresh_token = generate_token()
            expires = timezone.now() + timedelta(seconds=oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS)

            access_token = AccessToken.objects.create(
                user=user,
                application=app,
                expires=expires,
                token=token,
                scope='read write'
            )

            refresh_token = RefreshToken.objects.create(
                user=user,
                token=refresh_token,
                application=app,
                access_token=access_token
            )

            update_last_login(None, user)

            return Response({
                'access_token': access_token.token,
                'refresh_token': refresh_token.token,
                'expires_in': oauth2_settings.ACCESS_TOKEN_EXPIRE_SECONDS
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class UserSearchView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        keyword = self.request.query_params.get('search', '').lower()
        if '@' in keyword:
            return User.objects.filter(email__iexact=keyword)
        return User.objects.filter(
            Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(username__icontains=keyword)
        )

class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from_user = request.user
        to_user_id = request.data.get('to_user_id')
        try:
            to_user = User.objects.get(id=to_user_id)
        except User.DoesNotExist:
            return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
        if from_user == to_user :
            return Response({'error': 'Cannot send friend request to yourself'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if they are already friends
        print("friends: ",FriendRequest.objects.filter(Q(from_user=from_user, accepted=True) | Q(to_user=from_user, accepted=True)))
        friends = FriendRequest.objects.filter(Q(from_user=from_user, accepted=True) | Q(to_user=from_user, accepted=True))
        friend_ids = [fr.to_user.id if fr.from_user == from_user else fr.from_user.id for fr in friends]
        print("ids: ",friend_ids)
        print("to user id: ", to_user_id)
        if int(to_user_id) in friend_ids:
            return Response({'error': 'Already friends'}, status=status.HTTP_400_BAD_REQUEST)
        
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
            return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
        one_minute_ago = timezone.now() - timedelta(minutes=1)
        if FriendRequest.objects.filter(from_user=from_user, timestamp__gte=one_minute_ago).count() >= 3:
            return Response({'error': 'Too many friend requests'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response({'message': 'Friend request sent'}, status=status.HTTP_201_CREATED)

class RespondFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, action):
        try:
            friend_request = FriendRequest.objects.get(id=pk, to_user=request.user)
        except FriendRequest.DoesNotExist:
            return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

        if action == 'accept':
            friend_request.accepted = True
            friend_request.save()
            return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)
        elif action == 'reject':
            friend_request.delete()
            return Response({'message': 'Friend request rejected'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

class ListFriendsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserSerializer

    def get_queryset(self):
        user = self.request.user
        friends = FriendRequest.objects.filter(Q(from_user=user, accepted=True) | Q(to_user=user, accepted=True))
        friend_ids = [fr.to_user.id if fr.from_user == user else fr.from_user.id for fr in friends]
        return User.objects.filter(id__in=friend_ids)

class ListPendingRequestsView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = FriendRequestSerializer

    def get_queryset(self):
        return FriendRequest.objects.filter(to_user=self.request.user, accepted=False)

# from django.shortcuts import render
# from django.contrib.auth import authenticate
# from django.core.exceptions import ValidationError
# from django.db.models import Q
# from django.utils import timezone
# from rest_framework import status, generics, views
# from rest_framework.permissions import IsAuthenticated
# from rest_framework.response import Response
# from rest_framework.authtoken.models import Token
# from .models import User, FriendRequest
# from .serializers import UserSerializer, FriendRequestSerializer
# import datetime

# # Create your views here.

# class WelcomeView(views.APIView):
#     def get(self, request):
#         return Response({'message': 'Welcome to social network.'}, status=status.HTTP_200_OK)
# class SignUpView(views.APIView):
#     def post(self, request):
#         data = request.data
#         try:
#             user = User.objects.create_user(
#                 username=data['email'],
#                 email=data['email'],
#                 password=data['password']
#             )
#             return Response({'message': 'User created successfully'}, status=status.HTTP_201_CREATED)
#         except Exception as e:
#             return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# class LoginView(views.APIView):
#     def post(self, request):
#         email = request.data.get('email').lower()
#         password = request.data.get('password')
#         user = authenticate(request, email=email, password=password)
#         print('user: ', user)
#         if user is not None:
#             token, created = Token.objects.get_or_create(user=user)
#             return Response({'token': token.key}, status=status.HTTP_200_OK)
#         return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

# class UserSearchView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserSerializer

#     def get_queryset(self):
#         keyword = self.request.query_params.get('search', '').lower()
#         print("keyword: ", keyword)
#         if '@' in keyword:
#             return User.objects.filter(email__iexact=keyword)
#         return User.objects.filter(
#             Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(username__icontains=keyword)
#         )

# class SendFriendRequestView(views.APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request):
#         from_user = request.user
#         to_user_id = request.data.get('to_user_id')
#         try:
#             to_user = User.objects.get(id=to_user_id)
#         except User.DoesNotExist:
#             return Response({'error': 'User does not exist'}, status=status.HTTP_404_NOT_FOUND)
        
#         if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists():
#             return Response({'error': 'Friend request already sent'}, status=status.HTTP_400_BAD_REQUEST)
        
#         one_minute_ago = timezone.now() - datetime.timedelta(minutes=1)
#         if FriendRequest.objects.filter(from_user=from_user, timestamp__gte=one_minute_ago).count() >= 3:
#             return Response({'error': 'Too many friend requests'}, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
#         FriendRequest.objects.create(from_user=from_user, to_user=to_user)
#         return Response({'message': 'Friend request sent'}, status=status.HTTP_201_CREATED)

# class RespondFriendRequestView(views.APIView):
#     permission_classes = [IsAuthenticated]

#     def post(self, request, pk, action):
#         try:
#             friend_request = FriendRequest.objects.get(id=pk, to_user=request.user)
#         except FriendRequest.DoesNotExist:
#             return Response({'error': 'Friend request not found'}, status=status.HTTP_404_NOT_FOUND)

#         if action == 'accept':
#             friend_request.accepted = True
#             friend_request.save()
#             return Response({'message': 'Friend request accepted'}, status=status.HTTP_200_OK)
#         elif action == 'reject':
#             friend_request.delete()
#             return Response({'message': 'Friend request rejected'}, status=status.HTTP_200_OK)
#         return Response({'error': 'Invalid action'}, status=status.HTTP_400_BAD_REQUEST)

# class ListFriendsView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserSerializer

#     def get_queryset(self):
#         user = self.request.user
#         friends = FriendRequest.objects.filter(Q(from_user=user, accepted=True) | Q(to_user=user, accepted=True))
#         friend_ids = [fr.to_user.id if fr.from_user == user else fr.from_user.id for fr in friends]
#         return User.objects.filter(id__in=friend_ids)

# class ListPendingRequestsView(generics.ListAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = FriendRequestSerializer

#     def get_queryset(self):
#         return FriendRequest.objects.filter(to_user=self.request.user, accepted=False)    
