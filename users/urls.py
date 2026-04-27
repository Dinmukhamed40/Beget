from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('account/', views.account, name='account'),
    path('about/', views.about, name='about'),
    path('quiz/', views.quiz, name='quiz'),
    path('mood/', views.mood, name='mood'),
    path('chat/', views.chat_bot, name='chat'),
]
