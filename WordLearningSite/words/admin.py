from django.contrib import admin
from .models import Word, QuizResult


class QuestionAdmin(admin.ModelAdmin): # 검색기능 추가
    search_fields = ['subject'] # 검색이라는 요소를 붙여서 확장한다.


admin.site.register(Word, QuestionAdmin)
admin.site.register(QuizResult)
