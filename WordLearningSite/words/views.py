from .models import Word,EnglishWord
from .forms import WordForm,EnglishWordForm
from django.contrib.auth.decorators import login_required
import random
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect

@login_required
def reset_words(request):
    # 사용자의 단어 리스트를 세션에 저장 (딕셔너리 형태로)
    words = list(Word.objects.filter(user=request.user).values('id', 'kanji', 'hiragana', 'definition'))
    request.session['remaining_words'] = words

@login_required
def word_list(request):
    words = Word.objects.filter(user=request.user)
    return render(request, 'words/word_list.html', {'words': words})

@login_required
def add_word(request):
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            word.user = request.user
            word.word_type = request.POST.get('new_word_type') or request.POST.get('word_type')
            word.save()
            messages.success(request, '단어가 성공적으로 추가되었습니다!')
            return redirect('words:word_list')
    else:
        form = WordForm()
    return render(request, 'words/add_word.html', {'form': form})

@login_required
def quiz_view(request):
    # 세션에서 단어 리스트를 가져오기
    remaining_words = request.session.get('remaining_words', [])

    if not remaining_words:  # 단어 리스트가 비어있으면 초기화
        reset_words(request)
        remaining_words = request.session['remaining_words']

    total_words = len(remaining_words)  # 총 단어 수

    if total_words < 3:
        return render(request, 'words/quiz.html', {
            'error_message': '퀴즈를 시작하려면 최소 3개의 단어가 필요합니다. 단어를 추가해주세요.'
        })

    correct_word_data = random.choice(remaining_words)
    other_words = [word for word in remaining_words if word['id'] != correct_word_data['id']]

    if len(other_words) < 2:
        return render(request, 'words/quiz.html', {
            'error_message': '퀴즈를 구성할 수 있는 단어가 부족합니다.'
        })

    selected_words = [correct_word_data] + random.sample(other_words, 2)
    random.shuffle(selected_words)

    remaining_words.remove(correct_word_data)  # 사용한 단어 제거
    request.session['remaining_words'] = remaining_words  # 업데이트된 단어 리스트 저장

    remaining_count = len(remaining_words)  # 남은 단어 수

    return render(request, 'words/quiz.html', {
        'selected_words': selected_words,
        'correct_word': correct_word_data,  # 딕셔너리 형태로 전달
        'total_words': total_words,
        'remaining_count': remaining_count,
    })

@login_required
def check_quiz(request):
    if request.method == 'POST':
        selected_definition = request.POST.get('selected_definition')  # 선택한 뜻
        correct_hiragana = request.POST.get('correct_hiragana')

        # 정답 단어를 DB에서 찾기 (히라가나로 검색)
        correct_word = Word.objects.filter(hiragana=correct_hiragana).first()

        # 정답 단어가 없을 경우, 히라가나만 반환
        if correct_word is None:
            return JsonResponse({
                'is_correct': False,
                'correct_hiragana': correct_hiragana,
                'correct_definition': None,
            })

        correct_definition = correct_word.definition
        is_correct = selected_definition == correct_definition

        return JsonResponse({
            'is_correct': is_correct,
            'correct_hiragana': correct_hiragana,
            'correct_definition': correct_definition,
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def quiz2_view(request):
    # 세션에서 단어 리스트를 가져오기
    remaining_words = request.session.get('remaining_words', [])

    if not remaining_words:  # 단어 리스트가 비어있으면 초기화
        reset_words(request)
        remaining_words = request.session['remaining_words']

    total_words = len(remaining_words)  # 총 단어 수

    if total_words < 3:
        return render(request, 'words/quiz2.html', {
            'error_message': '퀴즈를 시작하려면 최소 3개의 단어가 필요합니다. 단어를 추가해주세요.'
        })

    correct_word_data = random.choice(remaining_words)
    other_words = [word for word in remaining_words if word['id'] != correct_word_data['id']]

    if len(other_words) < 2:
        return render(request, 'words/quiz2.html', {
            'error_message': '퀴즈를 구성할 수 있는 단어가 부족합니다.'
        })

    selected_words = [correct_word_data] + random.sample(other_words, 2)
    random.shuffle(selected_words)

    remaining_words.remove(correct_word_data)  # 사용한 단어 제거
    request.session['remaining_words'] = remaining_words  # 업데이트된 단어 리스트 저장

    remaining_count = len(remaining_words)  # 남은 단어 수

    return render(request, 'words/quiz2.html', {
        'selected_words': selected_words,
        'correct_word': correct_word_data,  # 딕셔너리 형태로 전달
        'total_words': total_words,
        'remaining_count': remaining_count,
    })

@login_required
def check_quiz2(request):
    if request.method == 'POST':
        selected_definition = request.POST.get('selected_definition')  # 선택한 뜻
        correct_hiragana = request.POST.get('correct_hiragana')

        # 정답 단어를 DB에서 찾기 (히라가나로 검색)
        correct_word = Word.objects.filter(hiragana=correct_hiragana).first()

        # 정답 단어가 없을 경우, 히라가나만 반환
        if correct_word is None:
            return JsonResponse({
                'is_correct': False,
                'correct_hiragana': correct_hiragana,
                'correct_definition': None,
            })

        correct_definition = correct_word.definition
        is_correct = selected_definition == correct_definition

        return JsonResponse({
            'is_correct': is_correct,
            'correct_hiragana': correct_hiragana,
            'correct_definition': correct_definition,
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def word_list(request):
    words = Word.objects.filter(user=request.user)

    # 랜덤 단어 선택
    random_word = random.choice(words) if words.exists() else None

    return render(request, 'words/word_list.html', {
        'words': words,
        'random_word': random_word,
    })
    
@login_required
def reset_words_view(request):
    if request.method == 'POST':
        reset_words(request)  # 기존의 reset_words 함수를 호출
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

# 영어

@login_required
def english_word_list(request):
    words = EnglishWord.objects.all()  # 모든 영어 단어 가져오기
    random_word = words.order_by('?').first() if words else None  # 랜덤 단어
    return render(request, 'englishWords/english_word_list.html', {'words': words, 'random_word': random_word})

@login_required
def add_english_word(request):
    if request.method == 'POST':
        form = EnglishWordForm(request.POST)
        if form.is_valid():
            english_word = form.save(commit=False)  # 일단 객체 생성
            english_word.user = request.user  # 현재 사용자 할당
            english_word.save()  # 데이터베이스에 추가
            return redirect('words:english_word_list')  # 추가 후 리스트 페이지로 리다이렉트
    else:
        form = EnglishWordForm()
    return render(request, 'englishWords/add_english_word.html', {'form': form})

@login_required
def english_quiz_view(request):
    # 세션에서 단어 리스트를 가져오기
    remaining_words = request.session.get('remaining_english_words', [])

    if not remaining_words:  # 단어 리스트가 비어있으면 초기화
        reset_english_words(request)  # 초기화 함수 호출
        remaining_words = request.session['remaining_english_words']

    total_words = len(remaining_words)  # 총 단어 수

    if total_words < 3:
        return render(request, 'englishWords/english_quiz.html', {
            'error_message': '퀴즈를 시작하려면 최소 3개의 단어가 필요합니다. 단어를 추가해주세요.'
        })

    correct_word_data = random.choice(remaining_words)
    other_words = [word for word in remaining_words if word['id'] != correct_word_data['id']]

    if len(other_words) < 2:
        return render(request, 'englishWords/english_quiz.html', {
            'error_message': '퀴즈를 구성할 수 있는 단어가 부족합니다.'
        })

    selected_words = [correct_word_data] + random.sample(other_words, 2)
    random.shuffle(selected_words)

    remaining_words.remove(correct_word_data)  # 사용한 단어 제거
    request.session['remaining_english_words'] = remaining_words  # 업데이트된 단어 리스트 저장

    remaining_count = len(remaining_words)  # 남은 단어 수

    return render(request, 'englishWords/english_quiz.html', {
        'selected_words': selected_words,
        'correct_word': correct_word_data,
        'total_words': total_words,
        'remaining_count': remaining_count,
    })

@login_required
def meaning_quiz_view(request):
    # 세션에서 단어 리스트를 가져오기
    remaining_words = request.session.get('remaining_english_words', [])

    if not remaining_words:  # 단어 리스트가 비어있으면 초기화
        reset_english_words(request)  # 초기화 함수 호출
        remaining_words = request.session['remaining_english_words']

    total_words = len(remaining_words)  # 총 단어 수

    if total_words < 3:
        return render(request, 'englishWords/meaning_quiz.html', {
            'error_message': '퀴즈를 시작하려면 최소 3개의 단어가 필요합니다. 단어를 추가해주세요.'
        })

    correct_word_data = random.choice(remaining_words)
    other_words = [word for word in remaining_words if word['definition'] != correct_word_data['definition']]

    if len(other_words) < 2:
        return render(request, 'englishWords/meaning_quiz.html', {
            'error_message': '퀴즈를 구성할 수 있는 단어가 부족합니다.'
        })

    selected_words = [correct_word_data] + random.sample(other_words, 2)
    random.shuffle(selected_words)

    remaining_words.remove(correct_word_data)  # 사용한 단어 제거
    request.session['remaining_english_words'] = remaining_words  # 업데이트된 단어 리스트 저장

    remaining_count = len(remaining_words)  # 남은 단어 수

    return render(request, 'englishWords/meaning_quiz.html', {
        'selected_words': selected_words,
        'correct_word': correct_word_data,
        'total_words': total_words,
        'remaining_count': remaining_count,
    })

@login_required
def check_english_quiz(request):
    if request.method == 'POST':
        selected_word_id = request.POST.get('selected_word')
        remaining_words = request.session.get('remaining_english_words', [])

        # 선택한 단어와 나머지 단어에서 정답 찾기
        correct_word = next((word for word in remaining_words if word['id'] == int(selected_word_id)), None)

        if correct_word:
            is_correct = True  # 항상 정답으로 처리
            correct_definition = correct_word['definition']  # 정답의 뜻
            correct_word_text = correct_word['word']  # 정답의 단어

            return render(request, 'englishWords/quiz_result.html', {
                'is_correct': is_correct,
                'correct_word': correct_word_text,
                'correct_definition': correct_definition,
            })
        else:
            return render(request, 'englishWords/quiz_result.html', {
                'is_correct': False,
                'correct_word': None,
                'correct_definition': None,
            })
    else:
        return redirect('words:english_quiz')  # GET 요청 시 영어 퀴즈 페이지로 리다이렉트

@login_required
def reset_words_view(request):
    if request.method == 'POST':
        reset_english_words(request)  # 영어 단어 초기화 함수 호출
        return JsonResponse({'success': True})
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

@login_required
def reset_english_words(request):
    # 사용자의 영어 단어 리스트를 세션에 저장 (딕셔너리 형태로)
    words = list(EnglishWord.objects.filter(user=request.user).values('id', 'word', 'definition'))
    request.session['remaining_english_words'] = words  # 세션에 저장

@login_required
def check_meaning_quiz(request):
    if request.method == 'POST':
        selected_word_id = request.POST.get('selected_word')
        remaining_words = request.session.get('remaining_english_words', [])  # 올바른 세션 키로 변경

        # 선택한 단어와 나머지 단어에서 정답 찾기
        correct_word = next((word for word in remaining_words if word['id'] == int(selected_word_id)), None)

        if correct_word:
            # 선택한 단어의 뜻이 정답인지 확인
            selected_definition = request.POST.get('selected_definition')
            is_correct = (correct_word['definition'] == selected_definition)  # 정답 여부 확인
            correct_definition = correct_word['definition']  # 정답의 뜻
            correct_word_text = correct_word['word']  # 정답의 단어

            return render(request, 'englishWords/quiz_result.html', {
                'is_correct': is_correct,
                'correct_word': correct_word_text,
                'correct_definition': correct_definition,
            })
        else:
            return render(request, 'englishWords/quiz_result.html', {
                'is_correct': False,
                'correct_word': None,
                'correct_definition': None,
            })
    else:
        return redirect('words:meaning_quiz')  # GET 요청 시 뜻 퀴즈 페이지로 리다이렉트
