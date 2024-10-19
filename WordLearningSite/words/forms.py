from django import forms
from .models import Word

class WordForm(forms.ModelForm):
    class Meta:
        model = Word
        fields = ['kanji', 'hiragana', 'definition'] 
        labels = { # 내용
            'kanji': '한자',
            'hiragana': '히라가나/가타카나',
            'definition': '뜻',
        }