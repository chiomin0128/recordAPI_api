import jwt
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import AuthenticationFailed
from .models import User
from record_API.settings import SECRET_KEY


class AuthService:
    @staticmethod
    def get_user_from_token(token):
        token = token.split(" ")[1]
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
            user_id = payload.get('email')
            user = get_object_or_404(User, pk=user_id)
            return user
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Access token has expired')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
