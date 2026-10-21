from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from . import views

urlpatterns = [
    path('', views.home),


    # Маршруты для новостей
    path('news/', views.all_news, name='all_news'),
    path('news/<slug:slug>', views.get_news_page, name='get_news_page'),
    path('news/<int:pk>/edit/', views.news_edit, name='news_edit'),
    path('news/<int:pk>/delete/', views.news_delete_confirm, name='news_delete_confirm'),
    path('news/<int:pk>/delete/confirm/', views.news_delete, name='news_delete'),
    path('news/image/<int:image_id>/delete/', views.news_image_delete, name='news_image_delete'),

    # Маршруты для диспицлин
    path('disciplines/', views.disciplines, name='disciplines'),

    # Маршруты для авторизации/регистрации
    path('ajax/login/', views.ajax_login, name='ajax_login'),
    path('ajax/register/', views.ajax_register, name='ajax_register'),
    path('ajax/logout/', views.ajax_logout, name='ajax_logout'),
    path('ajax/password-reset/', views.ajax_password_reset, name='ajax_password_reset'),
    path('reset/<uidb64>/<token>/', views.reset_password_page, name='reset_password_page'),

    # Маршруты для профиля
    path('profile/<str:username>/', views.profile, name='profile'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
