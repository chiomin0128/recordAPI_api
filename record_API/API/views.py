import jwt
from rest_framework.views import APIView
from .serializers import *
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework import status
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.shortcuts import render, get_object_or_404
from record_API.settings import SECRET_KEY


class UserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class RegisterAPIView(APIView):
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # jwt 토큰 접근
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response(
                {
                    "user": serializer.data,
                    "message": "register success",
                    "token": {
                        "access": access_token,
                        "refresh": refresh_token,
                    },
                },
                status=status.HTTP_201_CREATED,
            )

            # jwt 토큰 => 쿠키에 저장
            res.set_cookie("access", access_token, httponly=True)
            res.set_cookie("refresh", refresh_token, httponly=True)

            return res
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthAPIView(APIView):
    permission_classes = [AllowAny]

    # 유저 정보 확인
    def get(self, request):
        try:
            # 헤더에서 access token을 가져옴
            access_token = request.headers.get('Authorization')
            if access_token is None:
                return Response({'error': 'Access token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
            access_token = access_token.split(" ")[1]

            # 토큰 디코딩해서 유저 정보 추출
            payload = jwt.decode(access_token, SECRET_KEY, algorithms=['HS256'])
            pk = payload.get('email')
            user = get_object_or_404(User, pk=pk)
            serializer = UserSerializer(instance=user)
            print("hello")
            return Response(serializer.data, status=status.HTTP_200_OK)

        except jwt.ExpiredSignatureError:
            # 토큰 만료 시 토큰 갱신
            refresh_token = request.COOKIES.get('refreshToken')
            if refresh_token is None:
                return Response({'error': 'Refresh token is missing'}, status=status.HTTP_401_UNAUTHORIZED)

            data = {'refresh': refresh_token}
            serializer = TokenRefreshSerializer(data=data)
            if serializer.is_valid(raise_exception=True):
                access = serializer.data.get('access')
                refresh = serializer.data.get('refresh')
                payload = jwt.decode(access, SECRET_KEY, algorithms=['HS256'])
                user_id = payload.get('user_id')
                user = get_object_or_404(User, pk=user_id)
                user_serializer = UserSerializer(instance=user)
                res = Response(user_serializer.data, status=status.HTTP_200_OK)
                res.set_cookie('accessToken', access, httponly=True)
                res.set_cookie('refreshToken', refresh, httponly=True)
                return res
            return Response({'error': 'Refresh token is invalid'}, status=status.HTTP_400_BAD_REQUEST)

        except jwt.InvalidTokenError:
            # 사용 불가능한 토큰일 때
            return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)


    # 로그인
    def post(self, request):
        user = authenticate(email=request.data.get("email"), password=request.data.get("password"))
        if user is not None:
            serializer = UserSerializer(user)
            token = TokenObtainPairSerializer.get_token(user)
            refresh_token = str(token)
            access_token = str(token.access_token)
            res = Response({
                "token": {
                    "accessToken": access_token,
                    "refreshToken": refresh_token,
                },
                "success": True
            }, status=status.HTTP_200_OK)
            res.set_cookie("accessToken", access_token, httponly=True)
            res.set_cookie("refreshToken", refresh_token, httponly=True)
            return res
        else:
            return Response({
                "msg": "계정을 찾을 수 없습니다.",
                "success": False
            }, status=status.HTTP_400_BAD_REQUEST)

    # 로그아웃
    def delete(self, request):
        response = Response({
            "message": "Logout success"
        }, status=status.HTTP_202_ACCEPTED)
        response.delete_cookie("accessToken")
        response.delete_cookie("refreshToken")
        return response