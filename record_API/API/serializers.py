from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            role=validated_data.get('role', ''),
            nickname=validated_data.get('nickname', ''),
            name=validated_data.get('name', ''),
            phone_number=validated_data.get('phone_number', ''),
            state=validated_data.get('state', 0),
            date=validated_data.get('date', None),
            kakaoID=validated_data.get('kakaoID', None),
            is_active=validated_data.get('is_active', True),
            is_staff=validated_data.get('is_staff', False),
            date_joined=validated_data.get('date_joined', None)
        )
        return user
