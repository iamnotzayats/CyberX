import json
from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required, permission_required
from django.utils import timezone
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.forms import SetPasswordForm
from django.utils.http import urlsafe_base64_decode

from .models import *
from .forms import NewsForm, DisciplineForm


# --- ГЛАВНАЯ ---
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


# --- НОВОСТИ ---
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

    return render(request, 'all_news.html', {
        'page_title': 'Все новости',
        'page_obj': page_obj,
    })


# --- ДИСЦИПЛИНЫ ---
def disciplines(request):
    disciplines_list = Disciplines.objects.all()
    return render(request, 'disciplines.html', {
        'page_title': 'Дисциплины',
        'disciplines': disciplines_list,
    })


# --- ПРОФИЛЬ ---
def profile(request, username):
    profile_user = get_object_or_404(Users, username=username)

    if request.user.is_authenticated:
        request.user.last_activity = timezone.now()
        request.user.save(update_fields=['last_activity'])

    if request.method == 'POST' and request.user == profile_user:
        if 'avatar' in request.FILES:
            profile_user.avatar = request.FILES['avatar']
            profile_user.save()
            messages.success(request, 'АВАТАР ОБНОВЛЕН!')
            return redirect('profile', username=username)

    return render(request, 'profile.html', {
        'page_title': f'Профиль — {profile_user.username}',
        'profile_user': profile_user,
    })


# --- AJAX АВТОРИЗАЦИЯ ---
def ajax_login(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            user = authenticate(request, username=data.get('username'), password=data.get('password'))
            if user is not None:
                login(request, user)
                return JsonResponse({'status': 'ok'})
            return JsonResponse({'status': 'error', 'message': 'НЕВЕРНЫЙ ЛОГИН ИЛИ ПАРОЛЬ'}, status=400)
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'ОШИБКА СЕРВЕРА'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'МЕТОД НЕ ПОДДЕРЖИВАЕТСЯ'}, status=405)


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

            user = Users.objects.create_user(username=username, email=email, password=password)
            login(request, user)
            return JsonResponse({'status': 'ok'})
        except Exception:
            return JsonResponse({'status': 'error', 'message': 'ОШИБКА РЕГИСТРАЦИИ'}, status=500)
    return JsonResponse({'status': 'error', 'message': 'МЕТОД НЕ ПОДДЕРЖИВАЕТСЯ'}, status=405)


def ajax_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'error', 'message': 'МЕТОД НЕ ПОДДЕРЖИВАЕТСЯ'}, status=405)


# --- ВОССТАНОВЛЕНИЕ ПАРОЛЯ ---
def ajax_password_reset(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            if not email:
                return JsonResponse({'status': 'error', 'message': 'ВВЕДИТЕ EMAIL'}, status=400)

            user = Users.objects.filter(email=email).first()
            if not user:
                return JsonResponse({'status': 'ok'})

            site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f"{site_url}/reset/{uid}/{token}/"

            subject = 'ВОССТАНОВЛЕНИЕ ПАРОЛЯ - CyberXGaming'
            text_content = f"Здравствуйте, {user.username}!\n\nСсылка для сброса пароля:\n{reset_link}"
            html_content = f"""
            <!DOCTYPE html><html><head><meta charset="utf-8"></head>
            <body style="margin:0;padding:0;background-color:#0b0014;font-family:'Courier New',monospace;color:#f0e6ff;">
                <table width="100%" cellpadding="0" cellspacing="0" style="padding:40px 10px;">
                    <tr><td align="center">
                        <table width="100%" style="max-width:600px;background-color:#14002a;border:3px solid #00ffff;padding:30px;">
                            <tr><td align="center" style="padding-bottom:20px;">
                                <h1 style="margin:0;font-size:20px;color:#ffff00;text-transform:uppercase;text-shadow:2px 2px 0 #ff00ff;">СБРОС ПАРОЛЯ</h1>
                            </td></tr>
                            <tr><td align="center"><div style="height:2px;background-color:#4a0080;width:100%;margin-bottom:20px;"></div></td></tr>
                            <tr><td style="font-size:16px;line-height:1.6;color:#a080c0;">
                                <p>Здравствуйте, <strong style="color: #00ffff;">{user.username}</strong>!</p>
                                <p>Вы запросили сброс пароля.</p>
                                <p style="margin-bottom:30px;">Нажмите на кнопку ниже, чтобы установить новый пароль:</p>
                            </td></tr>
                            <tr><td align="center" style="padding-bottom:30px;">
                                <a href="{reset_link}" style="display:inline-block;background-color:#ffff00;color:#0b0014;text-decoration:none;font-size:14px;font-weight:bold;padding:15px 25px;border:2px solid #ff00ff;">▶ СБРОСИТЬ ПАРОЛЬ</a>
                            </td></tr>
                            <tr><td align="center" style="font-size:12px;color:#604080;text-align:center;">
                                <p>Если вы не запрашивали сброс, проигнорируйте это письмо.</p>
                                <p style="margin-top:20px;color:#ff00ff;">CyberXGaming 🕹️</p>
                            </td></tr>
                        </table>
                    </td></tr>
                </table>
            </body></html>
            """
            msg = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [email])
            msg.attach_alternative(html_content, "text/html")
            msg.send()
            return JsonResponse({'status': 'ok'})
        except Exception:
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


# --- УПРАВЛЕНИЕ НОВОСТЯМИ ---
@permission_required('cyberxclient.add_news', raise_exception=True)
def news_create(request):
    if request.method == 'POST':
        form = NewsForm(request.POST, request.FILES)
        if form.is_valid():
            news = form.save()

            images = request.FILES.getlist('images')
            for img in images:
                NewsPicture.objects.create(news=news, image=img)

            messages.success(request, 'НОВОСТЬ УСПЕШНО СОЗДАНА!')
            return redirect('all_news')
    else:
        form = NewsForm()

    return render(request, 'news_add.html', {
        'form': form,
        'page_title': 'Создание новости'
    })


@permission_required('cyberxclient.change_news', raise_exception=True)
def news_edit(request, pk):
    news = get_object_or_404(News, pk=pk)

    if request.method == 'POST':
        form = NewsForm(request.POST, instance=news)
        if form.is_valid():
            form.save()

            images = request.FILES.getlist('images')
            for img in images:
                NewsPicture.objects.create(news=news, image=img)

            messages.success(request, 'НОВОСТЬ УСПЕШНО СОХРАНЕНА!')
            return redirect('news_edit', pk=news.pk)
    else:
        form = NewsForm(instance=news)

    return render(request, 'news_edit.html', {
        'form': form,
        'news': news,
        'page_title': f'Редактирование — {news.title}'
    })


@permission_required('cyberxclient.delete_news', raise_exception=True)
def news_delete_confirm(request, pk):
    news = get_object_or_404(News, pk=pk)
    return render(request, 'news_delete.html', {
        'news': news,
        'page_title': f'Удаление — {news.title}'
    })


@permission_required('cyberxclient.delete_news', raise_exception=True)
def news_delete(request, pk):
    news = get_object_or_404(News, pk=pk)
    if request.method == 'POST':
        news.delete()
        return redirect('all_news')
    return redirect('news_delete_confirm', pk=pk)


@permission_required('cyberxclient.change_news', raise_exception=True)
def news_image_delete(request, image_id):
    if request.method == 'POST':
        image = get_object_or_404(NewsPicture, id=image_id)
        news_id = image.news.id
        image.delete()
        return redirect('news_edit', pk=news_id)
    return redirect('home')


# --- УПРАВЛЕНИЕ ДИСЦИПЛИНАМИ ---
@permission_required('cyberxclient.add_disciplines', raise_exception=True)
def discipline_create(request):
    if request.method == 'POST':
        form = DisciplineForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'ДИСЦИПЛИНА ДОБАВЛЕНА!')
            return redirect('disciplines')
    else:
        form = DisciplineForm()

    return render(request, 'discipline_form.html', {
        'form': form,
        'title': 'ДОБАВЛЕНИЕ ДИСЦИПЛИНЫ',
        'is_edit': False
    })


@permission_required('cyberxclient.change_disciplines', raise_exception=True)
def discipline_edit(request, pk):
    discipline = get_object_or_404(Disciplines, pk=pk)

    if request.method == 'POST':
        form = DisciplineForm(request.POST, request.FILES, instance=discipline)
        if form.is_valid():
            form.save()
            messages.success(request, 'ДИСЦИПЛИНА ОБНОВЛЕНА!')
            return redirect('disciplines')
    else:
        form = DisciplineForm(instance=discipline)

    return render(request, 'discipline_form.html', {
        'form': form,
        'title': 'РЕДАКТИРОВАНИЕ ДИСЦИПЛИНЫ',
        'is_edit': True,
        'discipline': discipline
    })


@permission_required('cyberxclient.delete_disciplines', raise_exception=True)
def discipline_delete_confirm(request, pk):
    discipline = get_object_or_404(Disciplines, pk=pk)
    return render(request, 'discipline_delete.html', {
        'discipline': discipline,
        'page_title': f'Удаление — {discipline.name}'
    })


@permission_required('cyberxclient.delete_disciplines', raise_exception=True)
def discipline_delete(request, pk):
    discipline = get_object_or_404(Disciplines, pk=pk)
    if request.method == 'POST':
        discipline.delete()
        messages.success(request, 'ДИСЦИПЛИНА УДАЛЕНА!')
        return redirect('disciplines')
    return redirect('discipline_delete_confirm', pk=pk)