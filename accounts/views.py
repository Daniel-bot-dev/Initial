from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status
from django.contrib.auth import get_user_model, authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_yasg.utils import swagger_auto_schema
from .serializers import UserSerializer, LoginSerializer, OtpSerializer, ForgotPasswordSerializer, ResetPasswordSerializer
from .models import OTP
from .signals import generate_otp
from django.utils import timezone
import requests
from rest_framework_simplejwt.authentication import JWTAuthentication

User = get_user_model()

class LoginView(APIView):

    @swagger_auto_schema(request_body=LoginSerializer)

    def post(self, request):

        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request,
            email=serializer.validated_data.get('email'),
            password=serializer.validated_data.get('password')
        )

        if user:
            token_data = RefreshToken.for_user(user)
            data = {
                "name": user.full_name,
                "role": user.role,
                "refresh": str(token_data),
                "access": str(token_data.access_token)
            }
            return Response(data, status=200)
        return Response({"error": "Invalid credentials"}, status=400)

class UserGenericView(generics.ListCreateAPIView):

    authentication_classes = [JWTAuthentication]
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        User.objects.create_user(**serializer.validated_data)
        return Response(serializer.data, status=201)

    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return Response({"error": "Authentication credentials not valid"}, status=403)
        
        user = User.objects.all()
        return Response(UserSerializer(user, many=True).data, status=200)

class UserGenericByOne(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()
    lookup_field = 'pk'

class OtpVerifyView(APIView):

    @swagger_auto_schema(request_body=OtpSerializer)
    def post(self, request):

        serializer = OtpSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data['otp']

        if not OTP.objects.filter(otp=otp).exists():
            return Response({'error': 'Invalid OTP'}, status=404)
        otp_obj = OTP.objects.get(otp=otp)

        if otp_obj.is_otp_valid():
            otp_obj.user.is_active = True
            otp_obj.user.save()
            otp_obj.delete()

            return Response({'message': 'OTP verified successfully'}, status=200)
        else:
            otp_obj.delete()
            return Response({'error': 'OTP expired'}, status=400)


class ForgotPasswordView(APIView):

    @swagger_auto_schema(request_body=ForgotPasswordSerializer)
    def post(self, request):

        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=404)
        

        otp = generate_otp()
        expiry_date = timezone.now() + timezone.timedelta(minutes=10)

        OTP.objects.create(otp=otp, user=user, expiry_date=expiry_date)
        

        
        url = "https://api.useplunk.com/v1/track"
        header = {
            "Authorization": "Bearer sk_73e20053b8d7740e883642f612bb6cf42c53d79d60bec2fc",  # Use your real API key
            "Content-Type": "application/json"
        }

        data = {
            "email": user.email,
            "event": "forgot_password",  
            "data": {
                "full_name": user.full_name,
                "otp": str(otp)
            }
        }

        response = requests.post(
            url=url,
            headers=header,
            json=data
        )
        print(response.json())
                
        return Response({'message': 'OTP sent to your email'}, status=200)

class ResetPasswordView(APIView):

    @swagger_auto_schema(request_body=ResetPasswordSerializer)
    def post(self, request):

        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        otp = serializer.validated_data['otp']
        new_password = serializer.validated_data['new_password']

        try:
            otp_obj = OTP.objects.get(otp=otp)
        except OTP.DoesNotExist:
            return Response({'error': 'Invalid OTP'}, status=404)
        
        if not otp_obj.is_otp_valid():
            otp_obj.delete()
            return Response({'error': 'OTP expired'}, status=400)
        
        user = otp_obj.user
        user.set_password(new_password)
        user.save()
        otp_obj.delete()
        return Response({'message': 'Password reset successful'}, status=200)


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data["refresh"]
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({"message": "Logout successful"}, status=205)
        except Exception as e:
            return Response({"error": "Invalid token"}, status=400)





