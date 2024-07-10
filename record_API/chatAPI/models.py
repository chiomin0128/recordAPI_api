from django.db import models

class UserSetting(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.CharField(max_length=20)
    role = models.CharField(max_length=100)  # 호칭
    tone = models.CharField(max_length=100)  # 응답 방식
    goal = models.CharField(max_length=255)  # 목표 (기존 항목 유지)
    length = models.CharField(max_length=50)  # 응답 시간
    topics = models.CharField(max_length=50)  # 문화/취미
    mbti = models.CharField(max_length=4)  # MBTI (기존 항목 유지)
    pers = models.CharField(max_length=255)  # 기타 (기존 항목 유지)
    humor = models.CharField(max_length=50)  # 유머 감각
    engagement_level = models.CharField(max_length=50)  # 적극성
    synonym_usage = models.CharField(max_length=50)  # 동의어 사용 빈도
    emotion_detection = models.BooleanField(default=False)  # 감정 인식
    learning_feedback = models.BooleanField(default=False)  # 학습/피드백
    notification_frequency = models.CharField(max_length=50)  # 알림 빈도
    language_dialect = models.CharField(max_length=50)  # 언어 및 방언
    mood_adaptability = models.CharField(max_length=50)  # 사용자 기분 변화 대응

    class Meta:
        unique_together = (('id', 'user_id'),)

    def __str__(self):
        return str(self.user_id)

class ChatHistory(models.Model):
    chat_id = models.AutoField(primary_key=True)
    user_id = models.BigIntegerField()
    type = models.BooleanField(null=True, blank=True)
    message = models.CharField(max_length=255, null=True, blank=True)
    created_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = (('chat_id', 'user_id'),)

    def __str__(self):
        return str(self.chat_id)
