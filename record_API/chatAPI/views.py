from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from django.http import HttpResponse 
from rest_framework import status
from adrf.views import APIView
from rest_framework.response import Response  # 반드시 rest_framework.response.Response를 사용해야 합니다.
from rest_framework.permissions import IsAuthenticated

from chatAPI.serializers import UserSettingSerializer
from chatAPI.service import ChatService
from API.service import AuthService
from rest_framework.exceptions import AuthenticationFailed

# Create your views here.

def index(request):
    return HttpResponse("안녕하세요")



@method_decorator(csrf_exempt, name='dispatch')
class UserSettingView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        user_id = request.data.get('user_id')

        # user_id가 없으면 400 Bad Request 응답 반환
        if user_id is None:
            return Response({'error': 'user_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        try:
            # ChatService를 통해 user_setting을 조회
            user_setting = ChatService.manage_user_setting(user_id)
        except ValueError as e:
            # user_id가 존재하지 않으면 404 Not Found 응답 반환
            return Response({'error': str(e)}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = UserSettingSerializer(user_setting)
        return Response(serializer.data)

    def post(self, request, format=None):
        access_token = request.headers.get('Authorization')
        if not access_token:
            return Response({'error': 'Access token is missing'}, status=status.HTTP_401_UNAUTHORIZED)
        
        access_token = access_token.split(" ")[1]
        try:
            user = AuthService.get_user_from_token(access_token)
            data = request.data.copy()
            serializer = UserSettingSerializer(data=data)
            if serializer.is_valid():
                settings = serializer.validated_data
            
                user_setting = ChatService.manage_user_setting(user.user_id, settings)
                response_serializer = UserSettingSerializer(user_setting)
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except AuthenticationFailed as e:
            return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
        

@method_decorator(csrf_exempt, name='dispatch')
class SaveQuestionsView(APIView):
    def post(self, request, format=None):
        user_id = request.data.get('user_id')
        data = request.data
        print(data)

        result = ChatService.save_questions_to_vectordb(user_id, data)
        return Response(result, status=status.HTTP_201_CREATED)

@method_decorator(csrf_exempt, name='dispatch')
class ChatMessage(APIView):
    def post(self, request, format=None):
        user_id = request.data.get('user_id')
        user_message: str = request.data.get('user_message')
        print(user_message)
        print(type(user_message))
        result = ChatService.generate_response(user_id,user_message)
        return Response(result)
    def get(self, request, format=None):
        user_id = request.data.get('user_id')
        return Response(ChatService.chathistory(user_id))

