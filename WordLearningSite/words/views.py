from .models import Word, EnglishWord, QuizResult, VisitorCount
from django.db.models import Q
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

def quiz_view(request):
    current_count = request.session.get('current_count', 0)  # 기본값 0

def serialize_word(word):
    return {
        'id': word.id,
        'kanji': word.kanji,
        'hiragana': word.hiragana,
        'definition': word.definition,
        'unit': word.unit,
    }

def select_unit(request):
    units = Word.objects.values_list('unit', flat=True).distinct()  # 단원 목록 가져오기
    
    # 사용자가 선택한 단원 저장
    if request.method == 'POST':
        selected_unit = request.POST.get('unit')
        if selected_unit:
            request.session['selected_unit'] = selected_unit  # 세션에 선택한 단원 저장
            return redirect('words:unit_quiz_view')  # 퀴즈 페이지로 리다이렉트

    return render(request, 'words/select_unit.html', {'units': units})

def select_unit2(request):
    units = Word.objects.values_list('unit', flat=True).distinct()  # 단원 목록 가져오기
    
    # 사용자가 선택한 단원 저장
    if request.method == 'POST':
        selected_unit = request.POST.get('unit')
        if selected_unit:
            request.session['selected_unit2'] = selected_unit  # 세션에 선택한 단원 저장
            return redirect('words:unit_quiz_view2')  # 퀴즈 페이지로 리다이렉트

    return render(request, 'words/select_unit2.html', {'units': units})



def unit_quiz_view(request):
    if request.method == 'POST':
        unit = request.POST.get('unit')
        if unit:
            words = Word.objects.filter(unit=unit)
            if words.exists():
                request.session['remaining_japanese_words'] = list(words.values('id', 'kanji', 'hiragana', 'definition'))
                request.session['selected_unit'] = unit

                # current_count 초기화
                if 'current_count' not in request.session:
                    request.session['current_count'] = 0

                return redirect('words:quiz')
            else:
                messages.error(request, "선택한 단원에 단어가 없습니다.")

    return redirect('words:jp_unit_list')

def unit_quiz_view2(request):
    if request.method == 'POST':
        unit = request.POST.get('unit')  # 단원 정보를 POST로 가져옴
        if unit:
            words = Word.objects.filter(unit=unit)  # 선택한 단원의 단어들 가져오기
            if words.exists():
                # 단어 목록을 세션에 저장
                request.session['remaining_japanese_words'] = list(words.values('id', 'kanji', 'hiragana', 'definition'))
                request.session['selected_unit'] = unit  # 선택한 단원도 세션에 저장

                # current_count 초기화
                request.session['current_count'] = 0  # 기존에 'current_count'가 없으면 0으로 초기화

                return redirect('words:quiz2')  # 퀴즈 2 페이지로 리다이렉트
            else:
                messages.error(request, "선택한 단원에 단어가 없습니다.")  # 단어가 없을 경우 메시지 표시

    return redirect('words:jp_unit_list')  # POST가 아닐 경우 단원 목록으로 리다이렉트

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
    # 모든 일본어 단어 목록을 가져와 세션에 저장
    words = list(Word.objects.values('id', 'kanji', 'hiragana', 'definition'))
    request.session['remaining_japanese_words'] = words  # 세션에 저장

def reset_english_words(request):
    # 모든 영어 단어 목록을 가져와 세션에 저장
    words = list(EnglishWord.objects.values('id', 'word', 'definition'))
    request.session['remaining_english_words'] = words  # 세션에 저장

def reset_words_view(request):
    if request.method == 'POST' or request.method == 'GET':
        try:
            logger.info("reset_words_view 호출됨")  # 초기화 로그
            reset_japanese_words(request)
            reset_english_words(request)
            
            request.session['current_count'] = 0  # current_count 초기화
            
            return JsonResponse({'success': True})
        except Exception as e:
            logger.error(f"Exception in reset_words_view: {e}")
            return JsonResponse({'error': str(e)}, status=500)
    return JsonResponse({'error': 'Invalid request method.'}, status=400)


def word_list(request):
    # 요청에서 검색 쿼리를 가져옵니다.
    search_query = request.GET.get('search', '')  # 검색어가 없으면 빈 문자열로 기본 설정
    
    # 검색어가 있는 경우 필터링
    if search_query:
        words = Word.objects.filter(
            Q(kanji__icontains=search_query) |  # kanji 필드로 검색
            Q(hiragana__icontains=search_query) |  # hiragana 필드로 검색
            Q(definition__icontains=search_query)  # definition 필드로 검색
        )
    else:
        words = Word.objects.all()  # 검색어가 없으면 모든 단어 조회
    
    # 단어가 있으면 랜덤 단어 선택
    random_word = random.choice(words) if words.exists() else None  

    return render(request, 'words/word_list.html', {
        'words': words,
        'random_word': random_word,
        'search_query': search_query,  # 검색어를 템플릿에 전달 (선택적)
    })
@login_required
def add_word(request):
    # 기존 단원 목록 가져오기 (중복 제거)
    existing_units = Word.objects.values_list('unit', flat=True).distinct()  # 데이터베이스에서 단원 가져오기
    if request.method == 'POST':
        form = WordForm(request.POST)
        if form.is_valid():
            word = form.save(commit=False)
            word.user = request.user
            
            # 기존 단원 선택 또는 새 단원 추가 처리
            selected_unit = request.POST.get('unit') or request.POST.get('custom_unit', '기타')
            word.unit = selected_unit if selected_unit else '기타'  # 기본값 설정
            
            word.save()
            messages.success(request, '단어가 성공적으로 추가되었습니다!')
            return redirect('words:word_list')
    else:
        form = WordForm()
    
    return render(request, 'words/add_word.html', {'form': form, 'units': existing_units})

def quiz_view(request):
    unit = request.GET.get('unit', '전체')  # 선택된 단원 가져오기

    if unit == '전체':
        # 전체 단어 가져오기
        remaining_words = list(Word.objects.all())
    else:
        # 선택된 단원 단어 가져오기
        remaining_words = list(Word.objects.filter(unit=unit))

    # 전체 단어 수 설정
    total_words = len(remaining_words)

    # 단어 리스트가 비어있으면 초기화
    if not remaining_words:
        reset_japanese_words(request)  # 초기화 함수 호출
        remaining_words = list(Word.objects.all())  # 초기화 후 다시 가져오기
        total_words = len(remaining_words)  # 초기화 후 전체 단어 수 재설정
        # 초기화 메시지를 사용자에게 보여주기 위해 처리
        reset_message = '초기화 처리되었습니다.'  # 초기화 메시지 설정
    else:
        reset_message = None  # 초기화가 필요하지 않을 경우 메시지 없음

    # 세션에서 이미 사용한 단어 가져오기
    used_words = request.session.get('used_words', [])

    # 남은 단어에서 사용된 단어를 제외
    remaining_words = [word for word in remaining_words if word.id not in used_words]

    if len(remaining_words) < 3:  # 남은 단어가 3개 미만일 경우
        return render(request, 'words/quiz.html', {
            'error_message': '퀴즈를 시작하려면 최소 3개의 단어가 필요합니다. 단어를 추가해주세요.'
        })

    # 정답 단어 선택
    correct_word_data = random.choice(remaining_words)
    other_words = [word for word in remaining_words if word.id != correct_word_data.id]

    if len(other_words) < 2:  # 정답 외에 2개의 다른 단어가 필요
        return render(request, 'words/quiz.html', {
            'error_message': '퀴즈를 구성할 수 있는 단어가 부족합니다.'
        })

    selected_words = [correct_word_data] + random.sample(other_words, 2)
    random.shuffle(selected_words)

    # 사용한 단어 추가
    used_words.append(correct_word_data.id)
    request.session['used_words'] = used_words

    remaining_words.remove(correct_word_data)  # 사용한 단어 제거
    request.session['remaining_japanese_words'] = [serialize_word(word) for word in remaining_words]  # 직렬화하여 저장

    # 카운트 초기화 및 설정
    if 'current_count' not in request.session:
        request.session['current_count'] = 0  # 카운트 초기화는 여기서만

    current_count = request.session['current_count']  # 현재 카운트 가져오기

    # 남은 단어 수는 세션에서 가져온 남은 단어를 기준으로 설정
    remaining_count = total_words - current_count

    return render(request, 'words/quiz.html', {
        'selected_words': [serialize_word(word) for word in selected_words],  # 직렬화하여 전달
        'correct_word': serialize_word(correct_word_data),  # 직렬화하여 전달
        'total_words': total_words,  # 전체 단어 수
        'remaining_count': remaining_count,  # 수정된 남은 단어 수
        'current_count': current_count,  # 현재 카운트 전달
        'selected_unit': unit,  # 선택된 단원 전달
        'reset_message': reset_message  # 초기화 메시지 전달
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

        # 남은 단어 수는 세션에서 가져온 남은 단어를 기준으로 설정
        remaining_count = len(request.session.get('remaining_japanese_words', []))

        # 남은 단어 수가 0일 경우 초기화 요청
        if remaining_count == 0:
            reset_japanese_words(request)  # 초기화 호출
            remaining_count = len(request.session.get('remaining_japanese_words', []))  # 초기화 후 남은 단어 수 다시 계산
            return JsonResponse({
                'is_correct': is_correct,
                'correct_hiragana': correct_hiragana,
                'correct_definition': correct_definition,
                'remaining_count': remaining_count,  # 초기화 후 남은 단어 수
                'reset_quiz': True  # 초기화 요청 플래그 추가
            })

        # 정답일 경우에만 현재 카운트를 업데이트
        if is_correct:
            current_count = request.session['current_count']
            request.session['current_count'] = current_count + 1  # 카운트 증가

        return JsonResponse({
            'is_correct': is_correct,
            'correct_hiragana': correct_hiragana,
            'correct_definition': correct_definition,
            'remaining_count': remaining_count  # 남은 단어 수 반환
        })

    return JsonResponse({'error': 'Invalid request method.'}, status=400)

def get_new_word(request):
    if request.method == "GET":
        selected_words = list(Word.objects.all())
        if not selected_words:  # 단어가 없을 경우 처리
            return JsonResponse({'error': 'No words available.'}, status=404)

        new_word = random.choice(selected_words)  # 랜덤 단어 선택
        return JsonResponse({
            'new_word': new_word.kanji,
            'new_hiragana': new_word.hiragana,
            'new_definition': new_word.definition
        })

def quiz2_view(request):
    # 선택된 단원 가져오기 (기본값은 '전체')
    unit = request.GET.get('unit', '전체')

    # 전체 단어 또는 선택된 단원 단어 가져오기
    if unit == '전체':
        remaining_words = list(Word.objects.all())  # 전체 단어 가져오기
    else:
        remaining_words = list(Word.objects.filter(unit=unit))  # 선택된 단원 단어 가져오기

    if not remaining_words:  # 단어 리스트가 비어있으면 초기화
        reset_japanese_words(request)  # 초기화 함수 호출
        remaining_words = list(Word.objects.all())  # 초기화 후 다시 가져오기

    # 세션에서 이미 사용한 단어 가져오기
    used_words = request.session.get('used_words', [])

    # 남은 단어에서 사용된 단어를 제외
    remaining_words = [word for word in remaining_words if word.id not in used_words]

    total_words = len(remaining_words)  # 총 단어 수

    # 최소 3개 이상의 단어가 필요
    if total_words < 3:
        return render(request, 'words/quiz2.html', {
            'error_message': '퀴즈를 시작하려면 최소 3개의 단어가 필요합니다. 단어를 추가해주세요.'
        })

    # 정답 단어 선택
    correct_word_data = random.choice(remaining_words)
    other_words = [word for word in remaining_words if word.id != correct_word_data.id]

    # 다른 단어가 2개 이상인지 확인
    if len(other_words) < 2:
        return render(request, 'words/quiz2.html', {
            'error_message': '퀴즈를 구성할 수 있는 단어가 부족합니다.'
        })

    # 정답 단어와 랜덤으로 2개의 다른 단어 선택
    selected_words = [correct_word_data] + random.sample(other_words, 2)
    random.shuffle(selected_words)  # 단어 순서 섞기

    # 사용한 단어 추가
    used_words.append(correct_word_data.id)
    request.session['used_words'] = used_words

    remaining_words.remove(correct_word_data)  # 사용한 단어 제거
    request.session['remaining_japanese_words'] = [serialize_word(word) for word in remaining_words]  # 직렬화하여 저장

    remaining_count = len(remaining_words)  # 남은 단어 수 계산

    # 카운트 초기화 및 설정
    if 'current_count' not in request.session:
        request.session['current_count'] = 0  # 카운트 초기화는 여기서만

    current_count = request.session['current_count']  # 현재 카운트 가져오기
    remaining_count = total_words - current_count  # 남은 단어 수 계산

    # 퀴즈 화면 렌더링
    return render(request, 'words/quiz2.html', {
        'selected_words': [serialize_word(word) for word in selected_words],  # 직렬화하여 전달
        'correct_word': serialize_word(correct_word_data),  # 직렬화하여 전달
        'total_words': total_words,
        'remaining_count': remaining_count,  # 수정된 남은 단어 수
        'current_count': current_count,  # 현재 카운트 전달
        'selected_unit': unit  # 선택된 단원 전달
    })


def check_quiz2(request):
    if request.method == 'POST':
        selected_hiragana = request.POST.get('selected_hiragana')  # Get the selected hiragana
        correct_hiragana = request.POST.get('correct_hiragana')

        # Find the correct word in the database using hiragana
        correct_word = Word.objects.filter(hiragana=correct_hiragana).first()

        # If the correct word is not found, return the correct hiragana
        if correct_word is None:
            return JsonResponse({
                'is_correct': False,
                'correct_hiragana': correct_hiragana,
                'correct_definition': None,
            })

        correct_definition = correct_word.definition
        is_correct = selected_hiragana == correct_hiragana  # Compare the selected hiragana

        # Increment the current quiz count
        current_count = request.session.get('current_count', 0)
        request.session['current_count'] = current_count + 1  # Save the updated count

        return JsonResponse({
            'is_correct': is_correct,
            'correct_hiragana': correct_hiragana,
            'correct_definition': correct_definition,
            'current_count': request.session['current_count'],  # Return the current count
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
