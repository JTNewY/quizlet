from django import forms
from .models import Word,EnglishWord

class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['kanji', 'hiragana', 'definition'] 
        labels = { # 내용
            'kanji': '한자',
            'hiragana': '히라가나/가타카나',
            'definition': '뜻',
        }


class EnglishWordForm(forms.ModelForm):
    class Meta:
        model = EnglishWord
        fields = ['word', 'definition']  # 필요한 필드 추가
        labels = { # 내용
            'word': '영어단어',
            'definition': '뜻',
        }