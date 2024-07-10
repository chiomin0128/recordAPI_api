from rest_framework import serializers
from .models import UserSetting, ChatHistory

class UserSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserSetting
        exclude = ('user_id',)  # user_id 필드를 제외합니다.



class ChatHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatHistory
        fields = '__all__'