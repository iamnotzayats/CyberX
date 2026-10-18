from django.db.models import Prefetch
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator

from .models import *


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
    # Базовый queryset
    news_list = News.objects.prefetch_related(
        'badge', 'categories', 'pictures'
    ).order_by('-pub_date')

    # Пагинация
    paginator = Paginator(news_list, 3)  # 9 новостей на страницу (сетка 3x3)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_title': 'Все новости',
        'page_obj': page_obj,
    }
    return render(request, 'all_news.html', context)