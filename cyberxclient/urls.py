from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.home),


    # Маршруты для новостей
    path('news/', views.all_news, name='all_news'),
    path('news/<slug:slug>', views.get_news_page, name='get_news_page'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
