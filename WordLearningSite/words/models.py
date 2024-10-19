from django.db import models
from django.contrib.auth.models import User

class Word(models.Model):
    kanji = models.CharField(max_length=100, blank=True, null=True)  # 한자: null 및 빈 문자열 허용
    hiragana = models.CharField(max_length=100, blank=True, null=True)  # 히라가나 선택 사항
    definition = models.TextField()  # 뜻
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자와 연결

    def __str__(self):
        return self.kanji if self.kanji else (self.hiragana if self.hiragana else '')

class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)
