from django.urls import path

from . import views

urlpatterns = [
    path('api/', views.index),
    path('api/user-settings/', views.UserSettingView.as_view(), name='user_settings'),
    path('api/user-room/', views.ChatRoomList.as_view(), name='chat_room'),
    path('savequestions/', views.SaveQuestionsView.as_view(), name='save-questions'),
    path('qa/', views.ChatMessage.as_view(), name='qa'),
]