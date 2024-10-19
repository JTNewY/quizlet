from django.db import models
from django.contrib.auth.models import User

from django.db import models

class Word(models.Model):
    kanji = models.CharField(max_length=100)  # 한자
    hiragana = models.CharField(max_length=100, blank=True, null=True)  # 히라가나
    definition = models.TextField()  # 뜻
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 사용자와 연결

    def __str__(self):
        return self.kanji
    
class QuizResult(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.IntegerField()
    date_taken = models.DateTimeField(auto_now_add=True)