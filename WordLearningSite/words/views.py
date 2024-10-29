from .models import Word, EnglishWord, QuizResult, VisitorCount
from .forms import WordForm, EnglishWordForm
from django.contrib.auth.decorators import login_required
import random
from django.contrib import messages
from django.http import JsonResponse
from django.shortcuts import render, redirect
import json
import logging
from django.utils import timezone
from datetime import timedelta

logger = logging.getLogger(__name__)


def unit_quiz_view(request):
    if request.method == 'POST':
        unit = request.POST.get('unit')
        if unit:
            words = Word.objects.filter(unit=unit)  # 선택된 단원의 단어 가져오기
            request.session['remaining_japanese_words'] = list(words.values('id', 'kanji', 'hiragana', 'definition'))
            return redirect('words:quiz')  # 퀴즈 페이지로 리다이렉트
    return redirect('words:jp_unit_list')  # 단원이 없으면 단원 목록으로 리다이렉트

# 일본어 단원 목록
def jp_unit_list(request):
    units = Word.objects.values('unit').distinct()  # 일본어 단원 목록 가져오기
    words_by_unit = {unit['unit']: Word.objects.filter(unit=unit['unit']) for unit in units}  # 단원별 단어 목록
    return render(request, 'words/jp_unit_list.html', {'units': units, 'words_by_unit': words_by_unit})

# 일본어 단원 상세 페이지
def jp_unit_detail(request, unit):
    words = Word.objects.filter(unit=unit)  # 해당 일본어 단원에 있는 단어들
    return render(request, 'words/jp_unit_detail.html', {'unit': unit, 'words': words})

# 영어 단원 목록
def en_unit_list(request):
    units = EnglishWord.objects.values('unit').distinct()  # 영어 단원 목록 가져오기
    words_by_unit = {unit['unit']: EnglishWord.objects.filter(unit=unit['unit']) for unit in units}  # 단원별 단어 목록
    return render(request, 'words/en_unit_list.html', {'words_by_unit': words_by_unit})

# 영어 단원 상세 페이지
def en_unit_detail(request, unit):
    words = EnglishWord.objects.filter(unit=unit)  # 해당 영어 단원에 있는 단어들
    return render(request, 'words/en_unit_detail.html', {'unit': unit, 'words': words})

def update_visitor_count(request):
    # 세션이 만료되었는지 확인
    if 'last_visit' in request.session:
        last_visit = timezone.datetime.fromisoformat(request.session['last_visit'])  # ISO 포맷으로 변환
        if timezone.now() - last_visit < timedelta(minutes=30):  # 30분 이내에 방문
            return  # 카운트 증가 안 함
    
    # 새 방문으로 간주
    visitor, created = VisitorCount.objects.get_or_create(id=1)
    visitor.count += 1
    visitor.save()
    request.session['last_visit'] = timezone.now().isoformat()  # ISO 포맷 문자열로 저장

def main_page(request):
    update_visitor_count(request)  # request를 전달합니다.
    
    # 모든 일본어 단어와 영어 단어의 개수를 가져옴
    japanese_word_count = Word.objects.count()
    english_word_count = EnglishWord.objects.count()
    
    # 방문자 수 가져오기
    visitor_count = VisitorCount.objects.get(id=1).count

    # 템플릿에 전달할 컨텍스트 구성
    context = {
        'japanese_word_count': japanese_word_count,
        'english_word_count': english_word_count,
        'visitor_count': visitor_count,  # 방문자 수
    }
    
    return render(request, 'main/main_page.html', context)

def reset_japanese_words(request):
    # 모든 단어를 가져옴
    words = list(Word.objects.values('id', 'kanji', 'hiragana', 'definition'))
    request.session['remaining_japanese_words'] = words  # 세션에 저장

def reset_english_words(request):
    # 모든 단어를 가져옴
    words = list(EnglishWord.objects.values('id', 'word', 'definition'))
    request.session['remaining_english_words'] = words  # 세션에 저장

def reset_words_view(request):
    if request.method == 'POST':
        try:
            reset_japanese_words(request)  # 일본어 단어 리셋
            reset_english_words(request)    # 영어 단어 리셋

            # 유저가 로그인하지 않았을 때 QuizResult를 삭제할 필요가 없으므로 주석 처리
            # QuizResult.objects.filter(user=request.user).delete()  # 퀴즈 결과 초기화

            return JsonResponse({'success': True})

        except Exception as e:
            logger.error(f"Exception in reset_words_view: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def word_list(request):
    words = Word.objects.all()  # 모든 단어 조회
    random_word = random.choice(words) if words.exists() else None
    return render(request, 'words/word_list.html', {
        'words': words,
        'random_word': random_word,
    })

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

def quiz_view(request):
    
    remaining_words = request.session.get('remaining_japanese_words', [])

    if not remaining_words:  # 단어 리스트가 비어있으면 초기화
        reset_japanese_words(request)  # 초기화 함수 호출
        remaining_words = request.session['remaining_japanese_words']

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
    request.session['remaining_japanese_words'] = remaining_words  # 업데이트된 단어 리스트 저장

    remaining_count = len(remaining_words)  # 남은 단어 수

    return render(request, 'words/quiz.html', {
        'selected_words': selected_words,
        'correct_word': correct_word_data,
        'total_words': total_words,
        'remaining_count': remaining_count,
    })

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

def quiz2_view(request):
    remaining_words = request.session.get('remaining_japanese_words', [])

    if not remaining_words:  # 단어 리스트가 비어있으면 초기화
        reset_japanese_words(request)  # 초기화 함수 호출
        remaining_words = request.session['remaining_japanese_words']

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
    request.session['remaining_japanese_words'] = remaining_words  # 업데이트된 단어 리스트 저장

    remaining_count = len(remaining_words)  # 남은 단어 수

    return render(request, 'words/quiz2.html', {
        'selected_words': selected_words,
        'correct_word': correct_word_data,
        'total_words': total_words,
        'remaining_count': remaining_count,
    })

def check_quiz2(request):
    if request.method == 'POST':
        selected_hiragana = request.POST.get('selected_hiragana')  # 선택한 히라가나
        correct_hiragana = request.POST.get('correct_hiragana')

        # 정답 비교
        is_correct = selected_hiragana == correct_hiragana

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

        return JsonResponse({
            'is_correct': is_correct,
            'correct_hiragana': correct_hiragana,
            'correct_definition': correct_definition,
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def english_word_list(request):
    words = EnglishWord.objects.all()  # 모든 영어 단어 조회
    random_word = random.choice(words) if words.exists() else None
    return render(request, 'englishWords/english_word_list.html', {
        'words': words,
        'random_word': random_word,
    })

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

def english_quiz_view(request):
    # 세션에서 남은 영어 단어 목록 가져오기
    remaining_words = request.session.get('remaining_english_words', [])
    
    # 디버깅: 남은 단어 수 로그
    logger.debug(f'남은 단어 목록: {remaining_words}')

    # 남은 단어 목록이 없을 경우 초기화
    if not remaining_words:
        reset_english_words(request)  # 초기화 함수 호출
        remaining_words = request.session.get('remaining_english_words', [])
    
    # 디버깅: 초기화 후 남은 단어 수 로그
    logger.debug(f'초기화 후 남은 단어 목록: {remaining_words}')

    total_words = len(remaining_words)  # 총 단어 수 확인

    # 총 단어 수가 3개 미만일 경우 에러 메시지 반환
    if total_words < 3:
        return render(request, 'englishWords/english_quiz.html', {
            'error_message': '퀴즈를 시작하려면 최소 3개의 단어가 필요합니다. 단어를 추가해주세요.'
        })

    # 정답 단어 하나 선택
    correct_word_data = random.choice(remaining_words)
    
    # 정답이 아닌 다른 단어들 리스트 생성
    other_words = [word for word in remaining_words if word['id'] != correct_word_data['id']]

    # 선택 가능한 단어가 2개 미만일 경우 에러 메시지 반환
    if len(other_words) < 2:
        return render(request, 'englishWords/english_quiz.html', {
            'error_message': '퀴즈를 구성할 수 있는 단어가 부족합니다.'
        })

    # 정답 단어와 랜덤하게 선택한 다른 단어들 포함해서 퀴즈 리스트 구성
    selected_words = [correct_word_data] + random.sample(other_words, 2)
    random.shuffle(selected_words)

    # 사용한 단어 제거 후 세션 업데이트
    remaining_words.remove(correct_word_data)
    request.session['remaining_english_words'] = remaining_words

    remaining_count = len(remaining_words)  # 남은 단어 수 계산

    return render(request, 'englishWords/english_quiz.html', {
        'selected_words': selected_words,
        'correct_word': correct_word_data,  # ID와 함께 전달
        'total_words': total_words,
        'remaining_count': remaining_count,
    })

def check_english_quiz(request):
    if request.method == 'POST':
        correct_word = request.POST.get('correct_word')
        selected_definition = request.POST.get('selected_definition')
        correct_definition = request.POST.get('correct_definition')

        # 파라미터가 모두 있는지 확인
        if not correct_word or not selected_definition or not correct_definition:
            return JsonResponse({'is_correct': False, 'error': 'Missing parameters.'}, status=400)

        # 정답 확인 로직
        is_correct = selected_definition == correct_definition

        return JsonResponse({'is_correct': is_correct, 'correct_definition': correct_definition})
