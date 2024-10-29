import logging
from django.contrib import admin
from .models import Word, QuizResult, EnglishWord

logger = logging.getLogger(__name__)

class WordAdmin(admin.ModelAdmin):
    list_display = ('kanji', 'hiragana', 'definition', 'unit', 'user')
    search_fields = ('kanji', 'hiragana', 'definition', 'unit')
    list_filter = ('unit', 'user')
    list_editable = ('unit',)  # 'unit' 필드를 편집 가능하도록 설정

admin.site.register(Word, WordAdmin)
admin.site.register(EnglishWord)
admin.site.register(QuizResult)
