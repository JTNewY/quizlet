from django.urls import path
from . import views
from django.contrib.auth import views as auth_views
from .views import reset_words_view


app_name = 'words'

urlpatterns = [
    
    # 메인페이지
    path('main/',views.main_page, name='main'),
    
    # 로그인, 로그아웃 URL
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  
    path('logout/', auth_views.LogoutView.as_view(next_page='/words/main/'), name='logout'),
    
    # 일본어 관련 URL
    path('jp/', views.word_list, name='word_list'),  # 단어 목록 페이지
    path('jp_add/', views.add_word, name='add_word'),  # 단어 추가 페이지
    path('jp_quiz/', views.quiz_view, name='quiz'),  # 퀴즈 페이지
    path('jp_quiz/check/', views.check_quiz, name='check_quiz'),  # 퀴즈 결과 체크
    path('jp_quiz2/', views.quiz2_view, name='quiz2'),  # 퀴즈 2 페이지
    path('jp_quiz2/check/', views.check_quiz2, name='check_quiz2'),  # 퀴즈 2 결과 체크
    path('reset_words/', views.reset_words_view, name='reset_words'),
    path('select_unit/', views.select_unit, name='select_unit'),
    path('select_unit2/', views.select_unit2, name='select_unit2'),
    path('get_new_word/', views.get_new_word, name='get_new_word'),
    
    
    # 영어 관련 URL
    path('en/', views.english_word_list, name='english_word_list'),  # 영어 단어 목록 페이지
    path('en_add/', views.add_english_word, name='add_english_word'),  # 영어 단어 추가 페이지
    path('en_quiz/', views.english_quiz_view, name='english_quiz'),  # 영어 단어 퀴즈 페이지
    path('en_quiz/check/', views.check_english_quiz, name='check_english_quiz'),  # 영어 단어 퀴즈 결과 체크
    
      # 일본어 단원 목록 페이지
    path('jp/units/', views.jp_unit_list, name='jp_unit_list'),  # 일본어 단원 목록 페이지
    path('jp/unit/<str:unit>/', views.jp_unit_detail, name='jp_unit_detail'),  # 일본어 단원 상세 페이지
    
    # 영어 단원 목록 페이지
    path('en/units/', views.en_unit_list, name='en_unit_list'),  # 영어 단원 목록 페이지
    path('en/unit/<str:unit>/', views.en_unit_detail, name='en_unit_detail'),  # 영어 단원 상세 페이지
]
