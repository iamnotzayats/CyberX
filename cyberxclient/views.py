import json
import traceback
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.conf import settings
from django.urls import reverse
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode
from django.core.mail import EmailMultiAlternatives

from .models import *
from django.contrib.auth.decorators import login_required
from django.contrib import messages


def home(request):
    news = (
        News.objects
        .prefetch_related(
            'badge',
            'categories',
            Prefetch('pictures', queryset=NewsPicture.objects.order_by('id')),
        )
        .order_by('-pub_date')[:6]
    )
    return render(request, 'news.html', {
        'page_title': 'Home',
        'news': news,
    })


def get_news_page(request, slug):
    news = get_object_or_404(
        News.objects.prefetch_related(
            'badge', 'categories', Prefetch('pictures', queryset=NewsPicture.objects.order_by('id'))
        ),
        slug=slug
    )
    return render(request, 'news_page.html', context={'news': news})


def all_news(request):
    news_list = News.objects.prefetch_related(
        'badge', 'categories', 'pictures'
    ).order_by('-pub_date')

    paginator = Paginator(news_list, 9)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Все новости',
        'page_obj': page_obj,
    }
    return render(request, 'all_news.html', context)


def disciplines(request):
    disciplines_list = Disciplines.objects.all()
    return render(request, 'disciplines.html', {
        'page_title': 'Дисциплины',
        'disciplines': disciplines_list,
    })


# --- AJAX АВТОРИЗАЦИЯ ---
def ajax_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'ok'})
            else:
                return JsonResponse({'status': 'error', 'message': 'НЕВЕРНЫЙ ЛОГИН ИЛИ ПАРОЛЬ'}, status=400)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'ОШИБКА СЕРВЕРА'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'МЕТОД НЕ ПОДДЕРЖИВАЕТСЯ'}, status=405)


# --- AJAX РЕГИСТРАЦИЯ ---
def ajax_register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data.get('username')
            email = data.get('email')
            password = data.get('password')
            password_confirm = data.get('password_confirm')

            if password != password_confirm:
                return JsonResponse({'status': 'error', 'message': 'ПАРОЛИ НЕ СОВПАДАЮТ'}, status=400)

            if Users.objects.filter(username=username).exists():
                return JsonResponse({'status': 'error', 'message': 'ЭТОТ ЛОГИН УЖЕ ЗАНЯТ'}, status=400)

            if email and Users.objects.filter(email=email).exists():
                return JsonResponse({'status': 'error', 'message': 'ЭТА ПОЧТА УЖЕ ИСПОЛЬЗУЕТСЯ'}, status=400)

            user = Users.objects.create_user(
                username=username,
                email=email,
                password=password
            )
            user.save()

            login(request, user)
            return JsonResponse({'status': 'ok'})
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'ОШИБКА РЕГИСТРАЦИИ'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'МЕТОД НЕ ПОДДЕРЖИВАЕТСЯ'}, status=405)


# --- AJAX ВЫХОД ---
def ajax_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'МЕТОД НЕ ПОДДЕРЖИВАЕТСЯ'}, status=405)


def ajax_password_reset(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')

            if not email:
                return JsonResponse({'status': 'error', 'message': 'ВВЕДИТЕ EMAIL'}, status=400)

            user = Users.objects.filter(email=email).first()

            if not user:
                # Безопасность: не палим, что email не существует
                return JsonResponse({'status': 'ok'})

            site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{site_url}/reset/{uid}/{token}/"

            subject = 'ВОССТАНОВЛЕНИЕ ПАРОЛЯ - CyberXGaming'

            # 1. Обычный текст (если клиент не поддерживает HTML)
            text_content = f"""
            Здравствуйте, {user.username}!

            Вы запросили сброс пароля на сайте CyberXGaming.
            Чтобы установить новый пароль, перейдите по ссылке:
            {reset_link}

            Если вы не запрашивали сброс, просто проигнорируйте это письмо.
            """

            # 2. HTML-версия в аркадном стиле
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body style="margin: 0; padding: 0; background-color: #0b0014; font-family: 'Courier New', Courier, monospace; color: #f0e6ff;">
                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #0b0014; padding: 40px 10px;">
                    <tr>
                        <td align="center">
                            <!-- Само "окно" -->
                            <table width="100%" max-width="600" cellpadding="0" cellspacing="0" border="0" style="max-width: 600px; background-color: #14002a; border: 3px solid #00ffff; padding: 30px;">
                                <tr>
                                    <td align="center" style="padding-bottom: 20px;">
                                        <!-- Заголовок -->
                                        <h1 style="margin: 0; font-size: 20px; color: #ffff00; text-transform: uppercase; letter-spacing: 2px; text-shadow: 2px 2px 0 #ff00ff;">
                                            СБРОС ПАРОЛЯ
                                        </h1>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center">
                                        <div style="height: 2px; background-color: #4a0080; width: 100%; margin-bottom: 20px;"></div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="font-size: 16px; line-height: 1.6; color: #a080c0;">
                                        <p>Здравствуйте, <strong style="color: #00ffff;">{user.username}</strong>!</p>
                                        <p>Система зафиксировала запрос на сброс пароля для вашего аккаунта в <strong>CyberXGaming</strong>.</p>
                                        <p style="margin-bottom: 30px;">Если это были вы, нажмите на кнопку ниже, чтобы установить новый пароль:</p>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center" style="padding-bottom: 30px;">
                                        <!-- Кнопка -->
                                        <a href="{reset_link}" style="display: inline-block; background-color: #ffff00; color: #0b0014; text-decoration: none; font-size: 14px; font-weight: bold; padding: 15px 25px; border: 2px solid #ff00ff; box-shadow: 4px 4px 0 #00ffff;">
                                            ▶ СБРОСИТЬ ПАРОЛЬ
                                        </a>
                                    </td>
                                </tr>
                                <tr>
                                    <td align="center">
                                        <div style="height: 2px; background-color: #4a0080; width: 100%; margin-bottom: 20px;"></div>
                                    </td>
                                </tr>
                                <tr>
                                    <td style="font-size: 12px; color: #604080; text-align: center;">
                                        <p>Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо.</p>
                                        <p style="margin-top: 20px; color: #ff00ff;">CyberXGaming — Esports Arena 🕹️</p>
                                    </td>
                                </tr>
                            </table>

                            <!-- Подпись снизу -->
                            <div style="margin-top: 20px; font-size: 10px; color: #4a0080;">
                                PRESS START TO PLAY
                            </div>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

            # Отправка
            msg = EmailMultiAlternatives(
                subject,
                text_content,
                getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@cyberxgaming.ru'),
                [email]
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return JsonResponse({'status': 'ok'})

        except Exception as e:
            import traceback
            traceback.print_exc()
            return JsonResponse({'status': 'error', 'message': 'ОШИБКА СЕРВЕРА'}, status=500)

    return JsonResponse({'status': 'error', 'message': 'МЕТОД НЕ ПОДДЕРЖИВАЕТСЯ'}, status=405)


def reset_password_page(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = Users.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, Users.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        if request.method == 'POST':
            form = SetPasswordForm(user, request.POST)
            if form.is_valid():
                form.save()
                return render(request, 'password_reset_success.html')
        else:
            form = SetPasswordForm(user)

        return render(request, 'password_reset_confirm.html', {'form': form})
    else:
        return render(request, 'password_reset_invalid.html')



#@login_required(login_url='/')
def profile(request, username):
    profile_user = get_object_or_404(Users, username=username)

    if request.user.is_authenticated:
        request.user.last_activity = timezone.now()
        request.user.save(update_fields=['last_activity'])

    # 3. Передаем профиль этого пользователя в шаблон
    return render(request, 'profile.html', {
        'page_title': f'Профиль — {profile_user.username}',
        'profile_user': profile_user, # <-- Передаем того, чей профиль открыт
    })