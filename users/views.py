import json
import requests
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .forms import UserRegisterForm, UserUpdateForm, ProfileUpdateForm
from .models import Game, ChatMessage, BotKnowledge

# Константы API
DEEPSEEK_API_KEY = "sk-2c8d218540ef4cb6a24bbcdfdac80c1d"
DEEPSEEK_URL = "https://api.deepseek.com/chat/completions"


def home(request):
    games = Game.objects.all()
    return render(request, 'users/index.html', {'games': games})


def about(request):
    return render(request, 'users/about.html')


def quiz(request):
    return render(request, 'users/lab3.html')


def mood(request):
    return render(request, 'users/feedback.html')


def chat_bot(request):
    if request.method == 'POST':
        # Универсальное чтение — поддерживаем оба формата: JSON и form-urlencoded
        user_message = ''
        content_type = request.content_type or ''

        if 'application/json' in content_type:
            try:
                body = json.loads(request.body)
                user_message = body.get('message', '').strip()
            except (json.JSONDecodeError, AttributeError):
                pass
        else:
            # form-urlencoded (именно так отправляет script.js)
            user_message = request.POST.get('message', '').strip()

        if not user_message:
            return JsonResponse({'reply': 'Сообщение не может быть пустым.'})

        bot_reply = None

        # 1. Поиск в локальной базе знаний (SQLite)
        try:
            knowledge_items = BotKnowledge.objects.all()
            for item in knowledge_items:
                if item.keyword.lower() in user_message.lower():
                    bot_reply = item.answer
                    break
        except Exception as e:
            print(f"Ошибка базы знаний: {e}")

        # 2. Если в базе нет — запрос к DeepSeek AI
        if not bot_reply:
            try:
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
                }
                payload = {
                    "model": "deepseek-chat",
                    "messages": [
                        {
                            "role": "system",
                            "content": (
                                "Ты — ИИ-помощник штаба S.H.I.E.L.D. на игровом портале GamerVerse. "
                                "Отвечай кратко, по делу, на русском языке. "
                                "Можешь помогать с играми, советовать контент, отвечать на вопросы о Marvel и DC."
                            )
                        },
                        {"role": "user", "content": user_message}
                    ],
                    "max_tokens": 500,
                    "stream": False
                }
                response = requests.post(DEEPSEEK_URL, json=payload, headers=headers, timeout=20)
                print(f"DeepSeek статус: {response.status_code}")

                if response.status_code == 200:
                    result = response.json()
                    bot_reply = result['choices'][0]['message']['content']
                elif response.status_code == 401:
                    bot_reply = "Ошибка авторизации DeepSeek API. Проверь API-ключ в views.py."
                elif response.status_code == 402:
                    bot_reply = "Недостаточно средств на счёте DeepSeek. Пополни баланс на platform.deepseek.com."
                else:
                    bot_reply = f"Ошибка DeepSeek API (код {response.status_code}). Попробуй позже."

            except requests.exceptions.Timeout:
                bot_reply = "Сервер DeepSeek не ответил вовремя. Попробуй ещё раз."
            except requests.exceptions.ConnectionError:
                bot_reply = "Нет подключения к серверу DeepSeek. Проверь интернет."
            except Exception as e:
                print(f"Ошибка вызова ИИ: {e}")
                bot_reply = "Технические неполадки. Попробуй позже."

        # 3. Сохранение истории в SQLite
        current_user = request.user.username if request.user.is_authenticated else "Guest"
        try:
            ChatMessage.objects.create(
                user=current_user,
                question=user_message,
                answer=bot_reply
            )
        except Exception as e:
            print(f"Ошибка сохранения в БД: {e}")

        return JsonResponse({'reply': bot_reply})

    return redirect('home')


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})


@login_required
def account(request):
    if request.method == 'POST':
        u_form = UserUpdateForm(request.POST, instance=request.user)
        p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            p_form.save()
            return redirect('account')
    else:
        u_form = UserUpdateForm(instance=request.user)
        p_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'u_form': u_form,
        'p_form': p_form
    }
    return render(request, 'users/account.html', context)
