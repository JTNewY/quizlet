from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'words'

urlpatterns = [
    path('', views.word_list, name='word_list'),  # 단어 목록 페이지
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),  # 로그인 페이지
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),  # 로그아웃 페이지
    path('add/', views.add_word, name='add_word'),  # 단어 추가 페이지
    path('quiz/', views.quiz_view, name='quiz'),  # 퀴즈 페이지
    path('quiz/check/', views.check_quiz, name='check_quiz'),  # 퀴즈 결과 체크
    path('quiz2/', views.quiz2_view, name='quiz2'),  # 퀴즈 2 페이지
    path('quiz2/check/', views.check_quiz2, name='check_quiz2'),  # 퀴즈 2 결과 체크
]
