from django.db import models
from django.contrib.auth.models import User

class Word(models.Model):
    kanji = models.CharField(max_length=100, blank=True, null=True)
    hiragana = models.CharField(max_length=100, blank=True, null=True)
    definition = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unit = models.CharField(max_length=20, default='기타')  # 단원 필드 추가

    def __str__(self):
        return self.kanji if self.kanji else (self.hiragana if self.hiragana else '')

class EnglishWord(models.Model):
    word = models.CharField(max_length=100)
    definition = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    unit = models.CharField(max_length=20, default='기타')  # 단원 필드 추가

    def __str__(self):
        return self.word

class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='word_quiz_results')
    # 기타 필드 정의

class VisitorCount(models.Model):
    count = models.IntegerField(default=0)
