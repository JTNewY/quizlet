from .models import Word
from .forms import WordForm
from django.contrib.auth.decorators import login_required
import random
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404


def word_list(request):
    words = Word.objects.all()
    random_word = random.choice(words) if words else None  # 랜덤 단어 선택
    return render(request, 'words/word_list.html', {'words': words, 'random_word': random_word})

@login_required
def add_word(request):
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            word.user = request.user  # 현재 사용자와 단어 연결
            
            # 기존 타입 또는 새 타입 선택
            word.word_type = request.POST.get('new_word_type') or request.POST.get('word_type')
            
            word.save()
            messages.success(request, '단어가 성공적으로 추가되었습니다!')  # 성공 메시지 추가
            
            # 성공 시 단어 목록 페이지의 HTML을 직접 렌더링
            words = Word.objects.filter(user=request.user)
            return render(request, 'words/word_list.html', {'words': words})

    else:
        form = WordForm()
    return render(request, 'words/add_word.html', {'form': form})
@login_required
def quiz_view(request):
    words = Word.objects.filter(user=request.user)

    if words.count() < 3:
        return render(request, 'words/quiz.html', {
            'error_message': '퀴즈를 시작하려면 최소 3개의 단어가 필요합니다. 단어를 추가해주세요.'
        })

    # 단어 선택 로직
    correct_word = random.choice(words)
    other_words = list(words.exclude(id=correct_word.id))
    
    if len(other_words) < 2:
        return render(request, 'words/quiz.html', {
            'error_message': '퀴즈를 구성할 수 있는 단어가 부족합니다.'
        })

    selected_words = [correct_word] + random.sample(other_words, 2)
    random.shuffle(selected_words)

    return render(request, 'words/quiz.html', {
        'selected_words': selected_words,
        'correct_word': correct_word,
    })
    
@login_required
def check_quiz(request):
    if request.method == 'POST':
        selected_hiragana = request.POST.get('selected_hiragana')
        correct_hiragana = request.POST.get('correct_hiragana')

        # 정답 단어를 DB에서 찾기 (히라가나로 검색)
        correct_word = get_object_or_404(Word, hiragana=correct_hiragana)
        correct_definition = correct_word.definition

        # 선택한 히라가나가 정답과 일치하는지 확인
        is_correct = selected_hiragana == correct_hiragana

        if is_correct:
            message = '정답입니다!'
        else:
            message = f'틀렸습니다. 정답은 "{correct_hiragana}"입니다.'

        # JSON 응답에 정답 단어의 뜻을 포함시킴
        return JsonResponse({
            'is_correct': is_correct,
            'message': message,
            'correct_hiragana': correct_hiragana,
            'correct_definition': correct_definition,
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=400)
def get_quiz_choices(correct_word):
    # 모든 단어를 가져오고, 정답 단어는 제외
    words = list(Word.objects.exclude(id=correct_word.id))
    # 정답을 포함해 최대 3개의 단어를 랜덤으로 선택
    num_choices = min(3, len(words))  # 데이터베이스에 있는 단어가 적을 경우 예외 처리
    choices = random.sample(words, num_choices) if num_choices > 0 else []
    choices.append(correct_word)  # 정답 추가
    random.shuffle(choices)
    return choices

@login_required
def quiz2_view(request):
    # 현재 사용자에게 속한 단어를 가져옴
    words = Word.objects.filter(user=request.user)
    
    # 단어가 3개 이상인지 확인
    if words.count() < 3:
        return render(request, 'words/quiz2.html', {
            'error_message': '퀴즈를 시작하려면 최소 3개의 단어가 필요합니다. 단어를 추가해주세요.'
        })
    
    # 랜덤으로 정답 단어 선택
    correct_word = random.choice(words)
    
    # 정답 단어 외의 단어들 중에서 랜덤으로 2개 선택
    other_words = list(words.exclude(id=correct_word.id))
    if len(other_words) >= 2:
        other_words = random.sample(other_words, 2)
    else:
        return render(request, 'words/quiz2.html', {
            'error_message': '퀴즈를 구성할 수 있는 단어가 부족합니다.'
        })

    # 정답과 다른 단어들 합치기
    selected_words = [correct_word] + other_words

    # 무작위로 섞기
    random.shuffle(selected_words)

    return render(request, 'words/quiz2.html', {
        'selected_words': selected_words,
        'correct_word': correct_word,
    })

@login_required
def check_quiz2(request):
    if request.method == 'POST':
        selected_hiragana = request.POST.get('selected_hiragana')
        correct_hiragana = request.POST.get('correct_hiragana')

        # 정답 단어를 DB에서 찾기
        correct_word = get_object_or_404(Word, hiragana=correct_hiragana)
        correct_definition = correct_word.definition

        # 선택한 히라가나가 정답과 일치하는지 확인
        is_correct = selected_hiragana == correct_hiragana

        return JsonResponse({
            'is_correct': is_correct,
            'correct_hiragana': correct_hiragana,
            'correct_definition': correct_definition,
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=400)