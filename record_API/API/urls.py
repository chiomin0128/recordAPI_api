from django.urls import include, path
from rest_framework import routers
from rest_framework_simplejwt.views import TokenRefreshView

from .views import *

router = routers.DefaultRouter()
router.register('list', UserViewSet)  # 유저리스트 (테스트용)

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='register'),
    path("auth/", AuthAPIView.as_view(),  name='auth'),
    path("auth/refresh/", TokenRefreshView.as_view()),  # jwt 토큰 재발급
    path("", include(router.urls)),
]
